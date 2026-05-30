import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.database import init_db, get_connection

print("=== init_db ===")
init_db()

conn = get_connection()
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

# test simple ward insert
print("Inserting test ward...")
conn.execute("INSERT INTO wards (ward_number, ward_name) VALUES (999, 'Test Ward')")
conn.commit()
r = conn.execute("SELECT * FROM wards WHERE ward_number=999").fetchone()
print("Inserted:", dict(r) if r else "FAILED")
conn.close()
