from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import sqlite3
from ..database import get_db
from ..middleware.auth import verify_firebase_token

router = APIRouter()


@router.get("/citizen/stats")
def citizen_stats(
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = db.execute(
        """SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('submitted','under_review','assigned','in_progress','escalated','reopened') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) as resolved,
            ROUND(AVG(citizen_rating), 1) as avg_rating
           FROM complaints WHERE citizen_id = ?""",
        (user["id"],)
    ).fetchone()

    by_status = db.execute(
        "SELECT status, COUNT(*) as count FROM complaints WHERE citizen_id = ? GROUP BY status",
        (user["id"],)
    ).fetchall()

    by_category = db.execute(
        """SELECT cat.name, COUNT(*) as count
           FROM complaints c
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.citizen_id = ?
           GROUP BY cat.name""",
        (user["id"],)
    ).fetchall()

    trend = db.execute(
        """SELECT DATE(created_at) as date, COUNT(*) as count
           FROM complaints
           WHERE citizen_id = ? AND created_at >= DATE('now', '-7 days')
           GROUP BY DATE(created_at)
           ORDER BY date""",
        (user["id"],)
    ).fetchall()

    satisfaction_score = round(
        (stats["resolved"] or 0) / max(stats["total"], 1) * (stats["avg_rating"] or 0) / 5 * 100, 1
    ) if stats["total"] and stats["avg_rating"] else 0

    return {
        "total": stats["total"] or 0,
        "pending": stats["pending"] or 0,
        "resolved": stats["resolved"] or 0,
        "satisfaction_score": satisfaction_score,
        "avg_rating": stats["avg_rating"] or 0,
        "by_status": {r["status"]: r["count"] for r in by_status},
        "by_category": {r["name"]: r["count"] for r in by_category},
        "trend_last_7": [{"date": r["date"], "count": r["count"]} for r in trend]
    }


@router.get("/corporator/stats")
def corporator_stats(
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        """SELECT u.id,             u.ward_id, w.ward_name, w.ward_number, u.full_name
           FROM users u
           LEFT JOIN wards w ON u.ward_id = w.id
           WHERE u.firebase_uid = ?""",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ward_id = user["ward_id"]

    stats = db.execute(
        """SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('submitted','under_review','assigned','in_progress','escalated','reopened') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN sla_deadline < datetime('now') AND status NOT IN ('resolved','closed') THEN 1 ELSE 0 END) as overdue,
            ROUND(AVG(citizen_rating), 1) as satisfaction_score,
            ROUND(100.0 * SUM(CASE WHEN status IN ('resolved','closed') AND resolved_at <= sla_deadline THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END), 0), 1) as sla_compliance
           FROM complaints WHERE ward_id = ?""",
        (ward_id,)
    ).fetchone()

    by_category = db.execute(
        """SELECT cat.name, COUNT(*) as count
           FROM complaints c
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.ward_id = ?
           GROUP BY cat.name""",
        (ward_id,)
    ).fetchall()

    trend = db.execute(
        """SELECT DATE(created_at) as date, COUNT(*) as count
           FROM complaints
           WHERE ward_id = ? AND created_at >= DATE('now', '-30 days')
           GROUP BY DATE(created_at)
           ORDER BY date""",
        (ward_id,)
    ).fetchall()

    by_status = db.execute(
        "SELECT status, COUNT(*) as count FROM complaints WHERE ward_id = ? GROUP BY status",
        (ward_id,)
    ).fetchall()

    heatmap = db.execute(
        "SELECT location_lat, location_lng, status FROM complaints WHERE ward_id = ? AND location_lat IS NOT NULL",
        (ward_id,)
    ).fetchall()

    recent = db.execute(
        """SELECT c.*, u.full_name as citizen_name
           FROM complaints c
           JOIN users u ON c.citizen_id = u.id
           WHERE c.ward_id = ?
           ORDER BY c.created_at DESC LIMIT 20""",
        (ward_id,)
    ).fetchall()

    suggestions = db.execute(
        "SELECT COUNT(*) FROM suggestions WHERE ward_id = ?", (ward_id,)
    ).fetchone()[0]

    recent_suggestions = db.execute(
        """SELECT s.*, u.full_name as citizen_name
           FROM suggestions s
           JOIN users u ON s.citizen_id = u.id
           WHERE s.ward_id = ?
           ORDER BY s.created_at DESC LIMIT 10""",
        (ward_id,)
    ).fetchall()

    return {
        "ward_name": user["ward_name"],
        "ward_number": user["ward_number"],
        "corporator_name": user["full_name"],
        "total": stats["total"] or 0,
        "pending": stats["pending"] or 0,
        "resolved": stats["resolved"] or 0,
        "overdue": stats["overdue"] or 0,
        "satisfaction_score": stats["satisfaction_score"] or 0,
        "sla_compliance": stats["sla_compliance"] or 0,
        "total_suggestions": suggestions or 0,
        "by_status": {r["status"]: r["count"] for r in by_status},
        "by_category": {r["name"]: r["count"] for r in by_category},
        "trend_last_30": [{"date": r["date"], "count": r["count"]} for r in trend],
        "heatmap_data": [{"lat": r["location_lat"], "lng": r["location_lng"], "status": r["status"]} for r in heatmap],
        "recent_complaints": [dict(r) for r in recent],
        "recent_suggestions": [dict(r) for r in recent_suggestions]
    }


@router.get("/corporator/complaints")
def get_corporator_complaints(
    status: Optional[str] = Query(None),
    status_group: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute("SELECT ward_id FROM users WHERE firebase_uid = ?", (token_data["uid"],)).fetchone()
    if not user or not user["ward_id"]:
        return {"complaints": []}

    query = """SELECT c.*, u.full_name as citizen_name,
                      w.ward_number, w.ward_name
               FROM complaints c
               JOIN users u ON c.citizen_id = u.id
               JOIN wards w ON c.ward_id = w.id
               WHERE c.ward_id = ?"""
    params = [user["ward_id"]]

    if status:
        query += " AND c.status = ?"
        params.append(status)
    elif status_group == "pending":
        query += " AND c.status IN ('submitted','under_review','in_progress')"
    elif status_group == "resolved":
        query += " AND c.status IN ('resolved')"

    query += " ORDER BY c.created_at DESC"
    return {"complaints": [dict(r) for r in db.execute(query, params).fetchall()]}


@router.get("/notifications")
def get_notifications(
    db: sqlite3.Connection = Depends(get_db),
    token_data: dict = Depends(verify_firebase_token)
):
    user = db.execute(
        "SELECT id FROM users WHERE firebase_uid = ?",
        (token_data["uid"],)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rows = db.execute(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (user["id"],)
    ).fetchall()

    unread = db.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
        (user["id"],)
    ).fetchone()[0]

    return {"notifications": [dict(r) for r in rows], "unread_count": unread}
