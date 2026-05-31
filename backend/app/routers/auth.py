from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from ..database import get_db
from ..middleware.auth import verify_firebase_token
from ..services.gis_service import locate_ward
from .admin import _build_corporators, _build_representative

router = APIRouter()


class SendOTPRequest(BaseModel):
    mobile: str


class VerifyOTPRequest(BaseModel):
    session_id: str
    otp: str


class RegisterRequest(BaseModel):
    firebase_uid: str
    full_name: str
    mobile: str
    pin_code: str
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    ward_id: int | None = None


class ProfileResponse(BaseModel):
    user_id: int
    full_name: str
    mobile: str
    pin_code: str
    role: str
    ward: dict | None = None
    representatives: dict | None = None


class ProfileUpdateRequest(BaseModel):
    ward_id: int | None = None
    pin_code: str | None = None


def _get_profile(uid: str, db: sqlite3.Connection) -> dict:
    row = db.execute(
        """SELECT u.*, w.ward_name, w.ward_number,
                  w.mla_name, w.mla_constituency, w.mla_party,
                  w.mp_name, w.mp_constituency, w.mp_party,
                  w.corporator_a_name, w.corporator_a_party,
                  w.corporator_b_name, w.corporator_b_party,
                  w.corporator_c_name, w.corporator_c_party,
                  w.corporator_d_name, w.corporator_d_party
           FROM users u
           LEFT JOIN wards w ON u.ward_id = w.id
           WHERE u.firebase_uid = ?""",
        (uid,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    ward_id = row["ward_id"]
    reps = None
    if ward_id:
        fallback_names = {
            "corporator_a_name": row["corporator_a_name"], "corporator_a_party": row["corporator_a_party"],
            "corporator_b_name": row["corporator_b_name"], "corporator_b_party": row["corporator_b_party"],
            "corporator_c_name": row["corporator_c_name"], "corporator_c_party": row["corporator_c_party"],
            "corporator_d_name": row["corporator_d_name"], "corporator_d_party": row["corporator_d_party"],
        }
        reps = {
            "corporators": _build_corporators(db, ward_id, fallback_names),
            "mla": _build_representative(db, ward_id, row["mla_name"], row["mla_party"], "mla", row["mla_constituency"]),
            "mp": _build_representative(db, ward_id, row["mp_name"], row["mp_party"], "mp", row["mp_constituency"])
        }

    return {
        "user_id": row["id"],
        "full_name": row["full_name"],
        "mobile": row["mobile"],
        "pin_code": row["pin_code"],
        "role": row["role"],
        "is_verified": row["is_verified"] or 0,
        "ward": {
            "id": ward_id,
            "ward_number": row["ward_number"],
            "ward_name": row["ward_name"]
        } if ward_id else None,
        "representatives": reps
    }


@router.post("/register")
def register(req: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    ward_info = None
    ward_id = None

    if req.ward_id:
        ward_id = req.ward_id
        row = db.execute("SELECT id, ward_number, ward_name FROM wards WHERE id = ?", (ward_id,)).fetchone()
        if row:
            ward_info = dict(row)
    elif req.latitude and req.longitude:
        ward_info = locate_ward(req.latitude, req.longitude, db)
    elif req.pin_code:
        row = db.execute(
            "SELECT ward_id FROM pincode_ward_mapping WHERE pin_code = ? GROUP BY ward_id ORDER BY COUNT(*) DESC LIMIT 1",
            (req.pin_code,)
        ).fetchone()
        if row:
            ward_id = row["ward_id"]

    if ward_info:
        ward_id = ward_info["id"]

    try:
        db.execute(
            """INSERT INTO users (firebase_uid, full_name, mobile, pin_code, address, latitude, longitude, ward_id, role)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'citizen')""",
            (req.firebase_uid, req.full_name, req.mobile, req.pin_code,
             req.address, req.latitude, req.longitude, ward_id)
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")

    return _get_profile(req.firebase_uid, db)


@router.get("/profile")
def profile(
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    return _get_profile(token_data["uid"], db)


@router.patch("/profile")
def update_profile(
    req: ProfileUpdateRequest,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id FROM users WHERE firebase_uid = ?", (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    fields, vals = [], []
    if req.ward_id is not None:
        fields.append("ward_id = ?"); vals.append(req.ward_id)
    if req.pin_code is not None:
        fields.append("pin_code = ?"); vals.append(req.pin_code)
    if not fields:
        raise HTTPException(status_code=400, detail="Nothing to update")

    vals += ["CURRENT_TIMESTAMP", user["id"]]
    db.execute(
        f"UPDATE users SET {', '.join(fields)}, updated_at = ? WHERE id = ?", vals
    )
    db.commit()
    return _get_profile(token_data["uid"], db)


