import sqlite3


def create_notification(
    db: sqlite3.Connection,
    user_id: int,
    complaint_id: int,
    ntype: str,
    title: str,
    message: str,
    title_mr: str | None = None,
    message_mr: str | None = None,
    title_hi: str | None = None,
    message_hi: str | None = None
):
    db.execute(
        """INSERT INTO notifications
           (user_id, complaint_id, type, title, title_mr, title_hi, message, message_mr, message_hi)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, complaint_id, ntype, title, title_mr, title_hi, message, message_mr, message_hi)
    )
    db.commit()


def get_unread_count(db: sqlite3.Connection, user_id: int) -> int:
    row = db.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
        (user_id,)
    ).fetchone()
    return row[0]


def mark_as_read(db: sqlite3.Connection, notification_id: int, user_id: int):
    db.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (notification_id, user_id)
    )
    db.commit()
