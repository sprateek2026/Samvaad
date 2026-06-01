from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import sqlite3
import os
import uuid
from ..database import get_db
from ..middleware.auth import verify_firebase_token
from ..config import UPLOAD_DIR

router = APIRouter()

REP_PHOTO_DIR = os.path.join(UPLOAD_DIR, "representatives")
os.makedirs(REP_PHOTO_DIR, exist_ok=True)


class CreateUserRequest(BaseModel):
    firebase_uid: str
    full_name: str
    mobile: str
    pin_code: str = "411001"
    role: str
    ward_id: int | None = None


def require_admin(db, token_data):
    admin = db.execute(
        "SELECT role FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not admin or admin["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")


def rep_to_dict(r):
    return {
        "id": r["id"],
        "ward_id": r["ward_id"],
        "type": r["type"],
        "name": r["name"],
        "party": r["party"],
        "constituency": r["constituency"],
        "photo_path": r["photo_path"],
        "user_id": r["user_id"],
        "label": r["label"],
        "contact": r["contact"],
        "bio": r["bio"],
        "term": r["term"],
        "achievements": r["achievements"],
        "created_at": r["created_at"],
        "updated_at": r["updated_at"]
    }


@router.get("/representatives/{rep_id}/kyc")
def representative_kyc(
    rep_id: int,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    row = db.execute("""SELECT r.*, w.ward_number, w.ward_name
                        FROM representatives r
                        JOIN wards w ON r.ward_id = w.id
                        WHERE r.id = ?""", (rep_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Representative not found")
    return dict(row)


@router.post("/users")
def create_user(
    req: CreateUserRequest,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    resolved_ward_id = req.ward_id
    if req.ward_id is not None:
        ward = db.execute("SELECT id FROM wards WHERE ward_number = ?", (req.ward_id,)).fetchone()
        if not ward:
            raise HTTPException(status_code=400, detail=f"Ward number {req.ward_id} not found")
        resolved_ward_id = ward["id"]

    try:
        cur = db.execute(
            "INSERT INTO users (firebase_uid, full_name, mobile, pin_code, role, ward_id) VALUES (?, ?, ?, ?, ?, ?)",
            (req.firebase_uid, req.full_name, req.mobile, req.pin_code, req.role, resolved_ward_id)
        )
        if req.role == "corporator" and resolved_ward_id:
            db.execute(
                "UPDATE representative_mapping SET corporator_a_id = ? WHERE ward_id = ?",
                (cur.lastrowid, resolved_ward_id)
            )
        db.commit()
        return {"user_id": cur.lastrowid, "message": "User created"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User with this mobile or UID already exists")


@router.get("/complaints")
def all_complaints(
    ward_id: int | None = None,
    status: str | None = None,
    status_group: str | None = None,
    page: int = 1,
    limit: int = 100,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    base = """FROM complaints c
              JOIN users u ON c.citizen_id = u.id
              LEFT JOIN wards w ON c.ward_id = w.id
              WHERE 1=1"""
    params = []
    if ward_id:
        base += " AND c.ward_id = ?"
        params.append(ward_id)
    if status:
        base += " AND c.status = ?"
        params.append(status)
    elif status_group == "pending":
        base += " AND c.status IN ('submitted','under_review','assigned','in_progress','escalated','reopened')"
    elif status_group == "resolved":
        base += " AND c.status IN ('resolved','closed')"

    total = db.execute(f"SELECT COUNT(*) {base}", params).fetchone()[0]
    rows = db.execute(
        f"SELECT c.*, u.full_name as citizen_name, w.ward_number, w.ward_name {base}"
        f" ORDER BY c.created_at DESC LIMIT ? OFFSET ?",
        params + [limit, (page - 1) * limit]
    ).fetchall()
    return {
        "complaints": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/analytics/overview")
def analytics_overview(
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    total = db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    resolved = db.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('resolved','closed')").fetchone()[0]
    avg_time = db.execute(
        "SELECT ROUND(AVG(julianday(resolved_at) - julianday(created_at)) * 24, 1) FROM complaints WHERE resolved_at IS NOT NULL"
    ).fetchone()[0]
    sla = db.execute(
        "SELECT ROUND(100.0 * SUM(CASE WHEN resolved_at <= sla_deadline THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) FROM complaints WHERE resolved_at IS NOT NULL"
    ).fetchone()[0]

    by_ward = db.execute(
        """SELECT w.ward_name, COUNT(*) as count
           FROM complaints c JOIN wards w ON c.ward_id = w.id
           GROUP BY w.ward_name"""
    ).fetchall()

    return {
        "total_complaints": total,
        "resolved": resolved,
        "avg_resolution_time_hours": avg_time or 0,
        "sla_compliance": sla or 0,
        "by_ward": {r["ward_name"]: r["count"] for r in by_ward}
    }


def _build_corporators(db, ward_id, fallback_names):
    """Return all 4 corporator slots for a ward, falling back to static columns."""
    rows = db.execute(
        "SELECT id, name, party, photo_path, label FROM representatives WHERE ward_id = ? AND type = 'corporator' ORDER BY label",
        (ward_id,)
    ).fetchall()
    by_label = {r["label"]: {"id": r["id"], "name": r["name"], "party": r["party"], "photo_path": r["photo_path"]} for r in rows}

    labels = ["A", "B", "C", "D"]
    fallback_name_keys = ["corporator_a_name", "corporator_b_name", "corporator_c_name", "corporator_d_name"]
    fallback_party_keys = ["corporator_a_party", "corporator_b_party", "corporator_c_party", "corporator_d_party"]
    result = []
    for i, label in enumerate(labels):
        if label in by_label:
            result.append({
                "id": by_label[label]["id"],
                "name": by_label[label]["name"],
                "party": by_label[label]["party"] or fallback_names.get(fallback_party_keys[i]),
                "photo_path": by_label[label]["photo_path"],
                "label": label
            })
        else:
            result.append({
                "name": fallback_names.get(fallback_name_keys[i]),
                "party": fallback_names.get(fallback_party_keys[i]),
                "photo_path": None,
                "label": label
            })
    return result


def _build_representative(db, ward_id, fallback_name, fallback_party, rep_type, rep_constituency=None):
    """Build a representative dict from representatives table, falling back to wards columns."""
    row = db.execute(
        "SELECT name, party, constituency, photo_path FROM representatives WHERE ward_id = ? AND type = ?",
        (ward_id, rep_type)
    ).fetchone()
    if row:
        result = {"name": row["name"], "party": row["party"] or fallback_party, "photo_path": row["photo_path"]}
        if rep_type in ("mla", "mp"):
            result["constituency"] = row["constituency"] or rep_constituency
        return result
    result = {"name": fallback_name, "party": fallback_party, "photo_path": None}
    if rep_type in ("mla", "mp"):
        result["constituency"] = rep_constituency
    return result


# ─── Admin Dashboard ───────────────────────────────────────────────

@router.get("/dashboard")
def admin_dashboard(
    ward_id: int | None = None,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    base_where = ""
    params = []
    if ward_id:
        base_where = " WHERE c.ward_id = ?"
        params.append(ward_id)

    stats = db.execute(
        f"""SELECT
            COUNT(*) as total,
            SUM(CASE WHEN c.status IN ('submitted','under_review','assigned','in_progress','escalated','reopened') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN c.status IN ('resolved','closed') THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN c.sla_deadline < datetime('now') AND c.status NOT IN ('resolved','closed') THEN 1 ELSE 0 END) as overdue,
            ROUND(AVG(c.citizen_rating), 1) as satisfaction_score,
            ROUND(AVG(julianday(c.resolved_at) - julianday(c.created_at)) * 24, 1) as avg_resolution_time,
            ROUND(100.0 * SUM(CASE WHEN c.resolved_at <= c.sla_deadline THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN c.resolved_at IS NOT NULL THEN 1 ELSE 0 END), 0), 1) as sla_compliance
           FROM complaints c{base_where}""",
        params
    ).fetchone()

    by_ward = db.execute(
        """SELECT w.ward_name, COUNT(*) as count
           FROM complaints c JOIN wards w ON c.ward_id = w.id
           GROUP BY w.ward_name ORDER BY count DESC""",
    ).fetchall() if not ward_id else []

    by_category = db.execute(
        f"""SELECT cat.name, COUNT(*) as count
            FROM complaints c JOIN complaint_categories cat ON c.category_id = cat.id
            {base_where}
            GROUP BY cat.name ORDER BY count DESC""",
        params
    ).fetchall()

    by_status = db.execute(
        f"SELECT c.status, COUNT(*) as count FROM complaints c{base_where} GROUP BY c.status",
        params
    ).fetchall()

    trend = db.execute(
        f"""SELECT DATE(c.created_at) as date, COUNT(*) as count
            FROM complaints c
            {base_where + " AND" if base_where else "WHERE"}
            c.created_at >= DATE('now', '-30 days')
            GROUP BY DATE(c.created_at)
            ORDER BY date""",
        params
    ).fetchall()

    heatmap = db.execute(
        f"SELECT c.location_lat, c.location_lng, c.status FROM complaints c{base_where} AND c.location_lat IS NOT NULL"
        if base_where else
        "SELECT c.location_lat, c.location_lng, c.status FROM complaints c WHERE c.location_lat IS NOT NULL",
        params
    ).fetchall()

    recent = db.execute(
        f"""SELECT c.*, u.full_name as citizen_name, w.ward_number, w.ward_name
            FROM complaints c
            JOIN users u ON c.citizen_id = u.id
            LEFT JOIN wards w ON c.ward_id = w.id
            {base_where}
            ORDER BY c.created_at DESC LIMIT 200""",
        params
    ).fetchall()

    return {
        "total": stats["total"] or 0,
        "pending": stats["pending"] or 0,
        "resolved": stats["resolved"] or 0,
        "overdue": stats["overdue"] or 0,
        "avg_resolution_time": stats["avg_resolution_time"] or 0,
        "sla_compliance": stats["sla_compliance"] or 0,
        "satisfaction_score": stats["satisfaction_score"] or 0,
        "by_ward": [{"name": r["ward_name"], "count": r["count"]} for r in by_ward],
        "by_category": [{"name": r["name"], "count": r["count"]} for r in by_category],
        "by_status": [{"status": r["status"], "count": r["count"]} for r in by_status],
        "trend_last_30": [{"date": r["date"], "count": r["count"]} for r in trend],
        "heatmap_data": [{"lat": r["location_lat"], "lng": r["location_lng"], "status": r["status"]} for r in heatmap],
        "recent_complaints": [dict(r) for r in recent]
    }


# ─── Representative CRUD ──────────────────────────────────────────

@router.get("/representatives")
def list_representatives(
    ward_id: int | None = None,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    query = "SELECT * FROM representatives"
    params = []
    if ward_id:
        query += " WHERE ward_id = ?"
        params.append(ward_id)
    query += " ORDER BY type, label, id"
    rows = db.execute(query, params).fetchall()
    return {"representatives": [rep_to_dict(r) for r in rows]}


@router.post("/representatives")
def create_representative(
    ward_id: int = Form(...),
    type: str = Form(...),
    name: str = Form(...),
    party: str = Form(""),
    constituency: str = Form(""),
    label: str = Form(""),
    mobile: str = Form(""),
    contact: str = Form(""),
    bio: str = Form(""),
    term: str = Form(""),
    achievements: str = Form(""),
    photo: UploadFile | None = File(None),
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    if type not in ("corporator", "mla", "mp"):
        raise HTTPException(status_code=400, detail="Invalid type")

    ward = db.execute("SELECT id FROM wards WHERE id = ?", (ward_id,)).fetchone()
    if not ward:
        raise HTTPException(status_code=400, detail="Ward not found")

    label_val = label.upper() if label else None
    if type == "corporator":
        if label_val not in ("A", "B", "C", "D"):
            raise HTTPException(status_code=400, detail="Corporator label must be A, B, C, or D")
        existing = db.execute(
            "SELECT id FROM representatives WHERE ward_id = ? AND type = 'corporator' AND label = ?",
            (ward_id, label_val)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail=f"Corporator {label_val} already exists for this ward")
    else:
        existing = db.execute(
            "SELECT id FROM representatives WHERE ward_id = ? AND type = ?",
            (ward_id, type)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail=f"A {type} already exists for this ward")

    # If mobile provided, auto-create user account and link
    auto_user_id = None
    if mobile:
        firebase_uid = f"dev-user-{mobile}"
        existing_user = db.execute("SELECT id FROM users WHERE firebase_uid = ?", (firebase_uid,)).fetchone()
        if existing_user:
            auto_user_id = existing_user["id"]
        else:
            try:
                cur = db.execute(
                    "INSERT INTO users (firebase_uid, full_name, mobile, pin_code, role, ward_id) VALUES (?, ?, ?, ?, 'corporator', ?)",
                    (firebase_uid, name, mobile, "411001", ward_id)
                )
                auto_user_id = cur.lastrowid
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="User with this mobile already exists")
        # Ensure representative_mapping exists
        mapping = db.execute("SELECT id FROM representative_mapping WHERE ward_id = ?", (ward_id,)).fetchone()
        if mapping:
            db.execute(
                "UPDATE representative_mapping SET corporator_a_id = COALESCE(corporator_a_id, ?) WHERE ward_id = ?",
                (auto_user_id, ward_id)
            )
        else:
            db.execute(
                "INSERT OR IGNORE INTO representative_mapping (ward_id, corporator_a_id) VALUES (?, ?)",
                (ward_id, auto_user_id)
            )

    photo_path = None
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1] or ".jpg"
        fname = f"{uuid.uuid4()}{ext}"
        fpath = os.path.join(REP_PHOTO_DIR, fname)
        content = photo.file.read()
        with open(fpath, "wb") as f:
            f.write(content)
        photo_path = f"uploads/representatives/{fname}"

    cur = db.execute(
        """INSERT INTO representatives (ward_id, type, name, party, constituency, photo_path, user_id, label, contact, bio, term, achievements)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (ward_id, type, name, party or None, constituency or None, photo_path, auto_user_id, label_val, contact or None, bio or None, term or None, achievements or None)
    )
    db.commit()

    row = db.execute("SELECT * FROM representatives WHERE id = ?", (cur.lastrowid,)).fetchone()
    return rep_to_dict(row)


@router.put("/representatives/{rep_id}")
def update_representative(
    rep_id: int,
    name: str = Form(...),
    party: str = Form(""),
    constituency: str = Form(""),
    label: str = Form(""),
    mobile: str = Form(""),
    contact: str = Form(""),
    bio: str = Form(""),
    term: str = Form(""),
    achievements: str = Form(""),
    user_id: int | None = Form(None),
    photo: UploadFile | None = File(None),
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    existing = db.execute("SELECT * FROM representatives WHERE id = ?", (rep_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Representative not found")

    label_val = label.upper() if label else None
    if existing["type"] == "corporator" and label_val not in ("A", "B", "C", "D"):
        raise HTTPException(status_code=400, detail="Corporator label must be A, B, C, or D")

    # If mobile provided, create/get user and link
    resolved_user_id = user_id or existing["user_id"]
    if mobile:
        firebase_uid = f"dev-user-{mobile}"
        existing_user = db.execute("SELECT id FROM users WHERE firebase_uid = ?", (firebase_uid,)).fetchone()
        if existing_user:
            resolved_user_id = existing_user["id"]
        else:
            try:
                cur = db.execute(
                    "INSERT INTO users (firebase_uid, full_name, mobile, pin_code, role, ward_id) VALUES (?, ?, ?, ?, 'corporator', ?)",
                    (firebase_uid, name, mobile, "411001", existing["ward_id"])
                )
                resolved_user_id = cur.lastrowid
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="User with this mobile already exists")
        # Ensure representative_mapping exists
        mapping = db.execute("SELECT id FROM representative_mapping WHERE ward_id = ?", (existing["ward_id"],)).fetchone()
        if mapping:
            db.execute(
                "UPDATE representative_mapping SET corporator_a_id = COALESCE(corporator_a_id, ?) WHERE ward_id = ?",
                (resolved_user_id, existing["ward_id"])
            )
        else:
            db.execute(
                "INSERT OR IGNORE INTO representative_mapping (ward_id, corporator_a_id) VALUES (?, ?)",
                (existing["ward_id"], resolved_user_id)
            )

    photo_path = existing["photo_path"]
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1] or ".jpg"
        fname = f"{uuid.uuid4()}{ext}"
        fpath = os.path.join(REP_PHOTO_DIR, fname)
        content = photo.file.read()
        with open(fpath, "wb") as f:
            f.write(content)
        photo_path = f"uploads/representatives/{fname}"

        if existing["photo_path"]:
            old_path = os.path.join(UPLOAD_DIR, existing["photo_path"].replace("uploads/", ""))
            if os.path.exists(old_path):
                os.remove(old_path)

    db.execute(
        """UPDATE representatives SET name = ?, party = ?, constituency = ?, photo_path = ?, user_id = ?, label = ?, contact = ?, bio = ?, term = ?, achievements = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (name, party or None, constituency or None, photo_path, resolved_user_id, label_val, contact or None, bio or None, term or None, achievements or None, rep_id)
    )
    db.commit()

    row = db.execute("SELECT * FROM representatives WHERE id = ?", (rep_id,)).fetchone()
    return rep_to_dict(row)


@router.delete("/representatives/{rep_id}")
def delete_representative(
    rep_id: int,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    require_admin(db, token_data)

    existing = db.execute("SELECT * FROM representatives WHERE id = ?", (rep_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Representative not found")

    if existing["photo_path"]:
        old_path = os.path.join(UPLOAD_DIR, existing["photo_path"].replace("uploads/", ""))
        if os.path.exists(old_path):
            os.remove(old_path)

    db.execute("DELETE FROM representatives WHERE id = ?", (rep_id,))
    db.commit()
    return {"message": "Representative deleted"}


# ─── Representative CRUD ──────────────────────────────────────────
