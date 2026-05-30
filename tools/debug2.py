import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.database import init_db, get_connection

init_db()
conn = get_connection()

# Try INSERT without REPLACE
path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "pune-2022-wards.geojson")
features = json.load(open(path, encoding="utf-8"))["features"]
feat = features[0]
props = feat["properties"]
wn = props.get("wardnum") or props.get("prabhag_number") or props.get("ward_number")
n1 = props.get("Name1") or props.get("name1") or props.get("prabhag_name") or ""
n2 = props.get("Name2") or props.get("name2") or ""
wn2 = n2 if n2 else n1
print(f"Ward {wn}: {wn2}")
print(f"Geometry type: {feat['geometry']['type']}")

# Try simple INSERT
try:
    conn.execute("INSERT INTO wards (ward_number, ward_name, geometry) VALUES (?, ?, ?)", (int(wn), wn2, json.dumps(feat["geometry"])))
    conn.commit()
    print("INSERT succeeded")
except Exception as e:
    print(f"INSERT failed: {e}")

# Check if row exists
r = conn.execute("SELECT * FROM wards").fetchall()
print(f"Wards in table: {len(r)}")

# Try INSERT OR REPLACE
try:
    conn.execute("INSERT OR REPLACE INTO wards (ward_number, ward_name, geometry) VALUES (?, ?, ?)", (int(wn), wn2, json.dumps(feat["geometry"])))
    conn.commit()
    print("INSERT OR REPLACE succeeded")
except Exception as e:
    print(f"INSERT OR REPLACE failed: {e}")

conn.close()
