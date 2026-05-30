import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.database import init_db, get_connection

# Ensure no DB exists first
db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "samvaad.db")
if os.path.exists(db_path):
    os.remove(db_path)
for ext in ["-wal", "-shm"]:
    p = db_path + ext
    if os.path.exists(p):
        os.remove(p)

print("DB deleted:", not os.path.exists(db_path))

init_db()
conn = get_connection()

# Check if PRAGMA foreign_keys is on
fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
print(f"Foreign keys: {fk}")

# Check the wards table schema
schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='wards'").fetchone()[0]
print(f"Wards schema: {schema}")

# Try INSERT with explicit values
try:
    conn.execute("INSERT INTO wards (ward_number, ward_name) VALUES (1, 'Test')")
    conn.commit()
    print("Simple INSERT succeeded")
except Exception as e:
    print(f"Simple INSERT failed: {e}")

r = conn.execute("SELECT COUNT(*) FROM wards").fetchone()[0]
print(f"Wards count: {r}")
conn.close()
