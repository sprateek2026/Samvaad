import sqlite3
import json


def _rep_photos(db, ward_id):
    rows = db.execute(
        "SELECT type, label, photo_path FROM representatives WHERE ward_id = ? AND photo_path IS NOT NULL",
        (ward_id,)
    ).fetchall()
    return {f"{r['type']}_{r['label'] or ''}": r["photo_path"] for r in rows}


def _build_corporators_gis(db, ward_id, fallback_names):
    rows = db.execute(
        "SELECT name, party, photo_path, label FROM representatives WHERE ward_id = ? AND type = 'corporator' ORDER BY label",
        (ward_id,)
    ).fetchall()
    by_label = {r["label"]: {"name": r["name"], "party": r["party"], "photo_path": r["photo_path"]} for r in rows}
    labels = ["A", "B", "C", "D"]
    nk = ["corporator_a_name", "corporator_b_name", "corporator_c_name", "corporator_d_name"]
    pk = ["corporator_a_party", "corporator_b_party", "corporator_c_party", "corporator_d_party"]
    result = []
    for i, label in enumerate(labels):
        if label in by_label:
            result.append({
                "name": by_label[label]["name"],
                "party": by_label[label]["party"] or fallback_names.get(pk[i]),
                "photo_path": by_label[label]["photo_path"],
                "label": label
            })
        else:
            result.append({
                "name": fallback_names.get(nk[i]),
                "party": fallback_names.get(pk[i]),
                "photo_path": None,
                "label": label
            })
    return result


def locate_ward(latitude: float, longitude: float, db: sqlite3.Connection) -> dict | None:
    rows = db.execute("SELECT id, geometry FROM wards WHERE geometry IS NOT NULL").fetchall()

    point = {"type": "Point", "coordinates": [longitude, latitude]}

    for row in rows:
        try:
            geom = json.loads(row["geometry"])
            if point_in_polygon(point, geom):
                ward = db.execute(
                    """SELECT id, ward_number, ward_name, ward_name_mr,
                              corporator_a_name, corporator_a_party,
                              corporator_b_name, corporator_b_party,
                              corporator_c_name, corporator_c_party,
                              corporator_d_name, corporator_d_party,
                              mla_name, mla_constituency, mla_party,
                              mp_name, mp_constituency, mp_party
                       FROM wards WHERE id = ?""",
                    (row["id"],)
                ).fetchone()
                if ward:
                    photos = _rep_photos(db, ward["id"])
                    fallback = {
                        "corporator_a_name": ward["corporator_a_name"], "corporator_a_party": ward["corporator_a_party"],
                        "corporator_b_name": ward["corporator_b_name"], "corporator_b_party": ward["corporator_b_party"],
                        "corporator_c_name": ward["corporator_c_name"], "corporator_c_party": ward["corporator_c_party"],
                        "corporator_d_name": ward["corporator_d_name"], "corporator_d_party": ward["corporator_d_party"],
                    }
                    return {
                        "id": ward["id"],
                        "ward_number": ward["ward_number"],
                        "ward_name": ward["ward_name"],
                        "ward_name_mr": ward["ward_name_mr"],
                        "corporators": _build_corporators_gis(db, ward["id"], fallback),
                        "mla": {
                            "name": ward["mla_name"],
                            "constituency": ward["mla_constituency"],
                            "party": ward["mla_party"],
                            "photo_path": photos.get("mla_")
                        },
                        "mp": {
                            "name": ward["mp_name"],
                            "constituency": ward["mp_constituency"],
                            "party": ward["mp_party"],
                            "photo_path": photos.get("mp_")
                        }
                    }
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    return None


def point_in_polygon(point: dict, polygon: dict) -> bool:
    try:
        coords = _get_coordinates(polygon)
        px, py = point["coordinates"]

        if not coords:
            return False

        inside = False
        for ring in coords:
            n = len(ring)
            j = n - 1
            for i in range(n):
                xi, yi = ring[i]
                xj, yj = ring[j]
                if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            if inside:
                return True

        return inside
    except Exception:
        return False


def _get_coordinates(geom: dict) -> list:
    if geom["type"] == "Polygon":
        return geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        coords = []
        for poly in geom["coordinates"]:
            coords.extend(poly)
        return coords
    return []
