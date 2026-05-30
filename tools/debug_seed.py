import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.database import init_db, get_connection

init_db()
conn = get_connection()

geojson_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "pune-2022-wards.geojson")
features = json.load(open(geojson_path, encoding="utf-8"))["features"]

for i, feat in enumerate(features):
    props = feat["properties"]
    wardnum = props.get("wardnum") or props.get("prabhag_number") or props.get("ward_number")
    name1 = props.get("Name1") or props.get("name1") or props.get("prabhag_name") or ""
    name2 = props.get("Name2") or props.get("name2") or ""
    ward_name = name2 if name2 else name1
    geom = json.dumps(feat["geometry"])
    try:
        conn.execute(
            "INSERT OR REPLACE INTO wards (ward_number, ward_name, geometry) VALUES (?, ?, ?)",
            (int(wardnum), ward_name, geom)
        )
        conn.commit()
    except Exception as e:
        print(f"FAIL on ward {wardnum} ({ward_name}): {e}")
        break

r = conn.execute("SELECT COUNT(*) FROM wards").fetchone()
print(f"Wards inserted: {r[0]}")
conn.close()
