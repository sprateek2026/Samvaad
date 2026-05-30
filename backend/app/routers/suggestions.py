from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from ..database import get_db
from ..middleware.auth import verify_firebase_token

router = APIRouter()


class SuggestionRequest(BaseModel):
    title: str
    description: str


@router.post("")
def create_suggestion(
    req: SuggestionRequest,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id, ward_id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cur = db.execute(
        "INSERT INTO suggestions (citizen_id, ward_id, title, description) VALUES (?, ?, ?, ?)",
        (user["id"], user["ward_id"], req.title, req.description)
    )
    db.commit()
    return {"suggestion_id": cur.lastrowid, "message": "Suggestion submitted"}


@router.get("")
def list_suggestions(
    ward_id: int | None = None,
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id, role, ward_id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == "citizen":
        rows = db.execute(
            "SELECT s.*, u.full_name as citizen_name FROM suggestions s JOIN users u ON s.citizen_id = u.id WHERE s.citizen_id = ? ORDER BY s.created_at DESC",
            (user["id"],)
        ).fetchall()
    elif user["role"] == "corporator":
        rows = db.execute(
            "SELECT s.*, u.full_name as citizen_name FROM suggestions s JOIN users u ON s.citizen_id = u.id WHERE s.ward_id = ? ORDER BY s.created_at DESC",
            (ward_id or user["ward_id"],)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT s.*, u.full_name as citizen_name FROM suggestions s JOIN users u ON s.citizen_id = u.id ORDER BY s.created_at DESC"
        ).fetchall()

    return {"suggestions": [dict(r) for r in rows]}
