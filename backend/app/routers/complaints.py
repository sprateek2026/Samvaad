from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from ..database import get_db
from ..middleware.auth import verify_firebase_token
from ..services.classifier import classify_complaint
from ..services.notification import create_notification
from ..config import UPLOAD_DIR

router = APIRouter()


class StatusUpdateRequest(BaseModel):
    status: str
    remarks: str = ""


class RatingRequest(BaseModel):
    rating: int


def generate_complaint_id(db: sqlite3.Connection) -> str:
    year = datetime.utcnow().year
    cur = db.execute("SELECT seq FROM complaint_id_seq WHERE year = ?", (year,))
    row = cur.fetchone()
    if row:
        seq = row["seq"] + 1
        db.execute("UPDATE complaint_id_seq SET seq = ? WHERE year = ?", (seq, year))
    else:
        seq = 1
        db.execute("INSERT INTO complaint_id_seq (year, seq) VALUES (?, ?)", (year, seq))
    db.commit()
    return f"SVD-{year}-{seq:04d}"


@router.post("")
def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    category_id: int | None = Form(None),
    sub_category_id: int | None = Form(None),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    location_address: str | None = Form(None),
    images: list[UploadFile] = File(default=[]),
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id, ward_id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not category_id:

        result = classify_complaint(title, description)
        category_row = db.execute(
            "SELECT id FROM complaint_categories WHERE name = ?",
            (result["category"].title(),)
        ).fetchone()
        if not category_row:
            category_row = db.execute(
                "SELECT id FROM complaint_categories WHERE name = 'Other'"
            ).fetchone()
        category_id = category_row["id"] if category_row else 1
        ai_category = result["category"]
        ai_confidence = result["confidence"]
        ai_method = result["method"]
    else:
        ai_category = None
        ai_confidence = None
        ai_method = None

    complaint_id = generate_complaint_id(db)
    sla_deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()

    ward_id = user["ward_id"]
    assigned_to = None
    if ward_id:
        corp = db.execute(
            "SELECT corporator_a_id FROM representative_mapping WHERE ward_id = ?",
            (ward_id,)
        ).fetchone()
        if corp and corp["corporator_a_id"]:
            assigned_to = corp["corporator_a_id"]

    cur = db.execute(
        """INSERT INTO complaints (complaint_id, citizen_id, category_id, sub_category_id, title, description,
           location_lat, location_lng, location_address, ward_id, assigned_to, status,
           ai_category, ai_confidence, ai_method, sla_deadline)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted', ?, ?, ?, ?)""",
        (complaint_id, user["id"], category_id, sub_category_id, title, description,
         latitude, longitude, location_address, ward_id, assigned_to,
         ai_category, ai_confidence, ai_method, sla_deadline)
    )
    db.commit()
    cid = cur.lastrowid

    db.execute(
        "INSERT INTO complaint_status_log (complaint_id, to_status, changed_by) VALUES (?, 'submitted', ?)",
        (cid, user["id"])
    )
    db.commit()

    for img in images:
        if img.filename:
            ext = os.path.splitext(img.filename)[1] or ".jpg"
            fname = f"{uuid.uuid4()}{ext}"
            fpath = os.path.join(UPLOAD_DIR, fname)
            content = img.file.read()
            with open(fpath, "wb") as f:
                f.write(content)
            db.execute(
                "INSERT INTO complaint_images (complaint_id, file_path, original_name, mime_type, file_size) VALUES (?, ?, ?, ?, ?)",
                (cid, f"uploads/{fname}", img.filename, img.content_type, len(content))
            )
    db.commit()

    if assigned_to:
        create_notification(
            db, assigned_to, cid, "new_complaint",
            "New Complaint Assigned",
            f"New complaint {complaint_id} assigned to you: {title[:50]}"
        )

    return {
        "complaint_id": complaint_id,
        "status": "submitted",
        "ai_classification": {
            "category": ai_category,
            "confidence": ai_confidence,
            "method": ai_method
        } if ai_category else None,
        "sla_deadline": sla_deadline
    }


@router.get("")
def list_complaints(
    status: str | None = None,
    status_group: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id, role, ward_id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    offset = (page - 1) * limit

    if user["role"] == "citizen":
        query = "SELECT c.*, u.full_name as citizen_name FROM complaints c JOIN users u ON c.citizen_id = u.id WHERE c.citizen_id = ?"
        params = [user["id"]]
    elif user["role"] == "corporator":
        query = "SELECT c.*, u.full_name as citizen_name FROM complaints c JOIN users u ON c.citizen_id = u.id WHERE c.assigned_to = ?"
        params = [user["id"]]
    else:
        query = "SELECT c.*, u.full_name as citizen_name FROM complaints c JOIN users u ON c.citizen_id = u.id WHERE 1=1"
        params = []

    if status:
        query += " AND c.status = ?"
        params.append(status)
    elif status_group == "pending":
        query += " AND c.status IN ('submitted','under_review','in_progress')"
    elif status_group == "resolved":
        query += " AND c.status IN ('resolved')"

    query += " ORDER BY c.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()

    count_query = "SELECT COUNT(*) FROM complaints c WHERE 1=1"
    count_params = []
    if user["role"] == "citizen":
        count_query += " AND c.citizen_id = ?"
        count_params.append(user["id"])
    elif user["role"] == "corporator":
        count_query += " AND c.assigned_to = ?"
        count_params.append(user["id"])

    if status:
        count_query += " AND c.status = ?"
        count_params.append(status)
    elif status_group == "pending":
        count_query += " AND c.status IN ('submitted','under_review','in_progress')"
    elif status_group == "resolved":
        count_query += " AND c.status IN ('resolved')"

    total = db.execute(count_query, count_params).fetchone()[0]

    return {"complaints": [dict(r) for r in rows], "total": total, "page": page}


@router.get("/{complaint_id}")
def get_complaint(
    complaint_id: str,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    row = db.execute(
        """SELECT c.*, u.full_name as citizen_name, u.mobile as citizen_mobile,
                  cat.name as category_name
           FROM complaints c
           JOIN users u ON c.citizen_id = u.id
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.complaint_id = ?""",
        (complaint_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Complaint not found")

    images = db.execute(
        "SELECT * FROM complaint_images WHERE complaint_id = ?",
        (row["id"],)
    ).fetchall()

    status_log = db.execute(
        """SELECT sl.*, u.full_name as changed_by_name
           FROM complaint_status_log sl
           LEFT JOIN users u ON sl.changed_by = u.id
           WHERE sl.complaint_id = ?
           ORDER BY sl.created_at DESC""",
        (row["id"],)
    ).fetchall()

    result = dict(row)
    result["images"] = [dict(i) for i in images]
    result["status_log"] = [dict(s) for s in status_log]
    return result


@router.patch("/{complaint_id}/status")
def update_status(
    complaint_id: str,
    req: StatusUpdateRequest,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id, role FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] not in ("corporator", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    complaint = db.execute(
        "SELECT * FROM complaints WHERE complaint_id = ?",
        (complaint_id,)
    ).fetchone()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    old_status = complaint["status"]
    db.execute(
        "UPDATE complaints SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE complaint_id = ?",
        (req.status, complaint_id)
    )
    db.execute(
        "INSERT INTO complaint_status_log (complaint_id, from_status, to_status, changed_by, remarks) VALUES (?, ?, ?, ?, ?)",
        (complaint["id"], old_status, req.status, user["id"], req.remarks)
    )
    db.commit()

    create_notification(
        db, complaint["citizen_id"], complaint["id"], "status_update",
        "Complaint Status Updated",
        f"Your complaint {complaint_id} is now {req.status}"
    )

    return {"message": "Status updated", "status": req.status}


@router.post("/{complaint_id}/rate")
def rate_complaint(
    complaint_id: str,
    req: RatingRequest,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()

    db.execute(
        "UPDATE complaints SET citizen_rating = ? WHERE complaint_id = ? AND citizen_id = ?",
        (req.rating, complaint_id, user["id"])
    )
    db.commit()
    return {"message": "Rating submitted"}
