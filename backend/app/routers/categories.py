from fastapi import APIRouter, HTTPException, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("")
def list_categories(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT id, name, name_mr, name_hi, routing_level, sla_hours FROM complaint_categories WHERE is_active = 1 ORDER BY id"
    ).fetchall()
    return {"categories": [dict(r) for r in rows]}


@router.get("/{category_id}/sub")
def list_sub_categories(category_id: int, db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT id, category_id, name, name_mr, name_hi FROM complaint_sub_categories WHERE category_id = ? AND is_active = 1 ORDER BY id",
        (category_id,)
    ).fetchall()
    return {"sub_categories": [dict(r) for r in rows]}
