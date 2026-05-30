import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.database import init_db, get_connection

init_db()
conn = get_connection()

print("Tables:", [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])

# seed wards
path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "pune-2022-wards.geojson")
features = json.load(open(path, encoding="utf-8"))["features"]
print(f"Inserting {len(features)} wards...")
for feat in features:
    props = feat["properties"]
    wn = props.get("wardnum") or props.get("prabhag_number") or props.get("ward_number")
    n1 = props.get("Name1") or props.get("name1") or props.get("prabhag_name") or ""
    n2 = props.get("Name2") or props.get("name2") or ""
    wn2 = n2 if n2 else n1
    conn.execute(
        "INSERT OR REPLACE INTO wards (ward_number, ward_name, geometry) VALUES (?, ?, ?)",
        (int(wn), wn2, json.dumps(feat["geometry"]))
    )
conn.commit()
print("Wards:", conn.execute("SELECT COUNT(*) FROM wards").fetchone()[0])

# import and run seed functions
from seed_database import seed_categories, seed_sub_categories, seed_representatives, seed_pincode_wards, seed_users
seed_representatives(conn)
seed_categories(conn)
seed_sub_categories(conn)
seed_pincode_wards(conn)
seed_users(conn)

cats = conn.execute("SELECT id, name FROM complaint_categories").fetchall()
print("Categories:", [dict(r) for r in cats])
subs = conn.execute("SELECT COUNT(*) FROM complaint_sub_categories").fetchone()[0]
print("Sub-categories count:", subs)
conn.close()
