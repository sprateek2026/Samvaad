import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "samvaad.db")
for ext in ["", "-wal", "-shm"]:
    p = db_path + ext
    if os.path.exists(p):
        os.remove(p)

from app.database import init_db, get_connection
init_db()
conn = get_connection()

# Check ALL wards
wards = conn.execute("SELECT id, ward_number, ward_name FROM wards ORDER BY ward_number").fetchall()
print(f"Total: {len(wards)}")
for w in wards:
    print(f"  id={w['id']} ward_number={w['ward_number']} name={w['ward_name']}")

conn.close()
