import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import init_db, get_connection

init_db()
conn = get_connection()

# Check WAL mode
mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
print(f"Journal mode: {mode}")

# Check if any data exists before we try
for table in ["wards", "complaint_categories", "complaint_sub_categories", "suggestions", "users"]:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")

# Try inserting one ward manually (not OR REPLACE)
try:
    conn.execute("INSERT INTO wards (ward_number, ward_name) VALUES (999, 'Manual Test')")
    conn.commit()
    print("Manual INSERT into wards: OK")
except Exception as e:
    print(f"Manual INSERT failed: {e}")

# Now try with a real feature from GeoJSON
path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "pune-2022-wards.geojson")
features = json.load(open(path, encoding="utf-8"))["features"]
feat = features[0]
props = feat["properties"]
wn = props.get("wardnum") or props.get("prabhag_number") or props.get("ward_number")
n1 = props.get("Name1") or props.get("name1") or props.get("prabhag_name") or ""
n2 = props.get("Name2") or props.get("name2") or ""
wn2 = n2 if n2 else n1

try:
    conn.execute("INSERT INTO wards (ward_number, ward_name, geometry) VALUES (?, ?, ?)", (int(wn), wn2, json.dumps(feat["geometry"])))
    conn.commit()
    print(f"INSERT ward {wn}: OK")
except Exception as e:
    print(f"INSERT ward {wn} failed: {e}")

# Try INSERT OR REPLACE with a new ward
try:
    conn.execute("INSERT OR REPLACE INTO wards (ward_number, ward_name, geometry) VALUES (?, ?, ?)", (998, "Replace Test", json.dumps(feat["geometry"])))
    conn.commit()
    print("INSERT OR REPLACE ward 998: OK")
except Exception as e:
    print(f"INSERT OR REPLACE ward 998 failed: {e}")

conn.close()
