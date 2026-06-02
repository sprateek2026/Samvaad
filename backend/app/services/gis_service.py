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


_WARD_CENTROIDS: dict | None = None


def ward_centroids(db: sqlite3.Connection) -> dict:
    """Return {ward_id: (lat, lng)} approximated from each ward's polygon by
    averaging its vertices. Used as a fallback location for complaints that have
    no explicit GPS coordinates, so the heatmap has a point for every complaint
    regardless of how it was seeded. Cached after first computation — ward
    geometry is static for the life of the process."""
    global _WARD_CENTROIDS
    if _WARD_CENTROIDS is not None:
        return _WARD_CENTROIDS

    out: dict = {}
    rows = db.execute("SELECT id, geometry FROM wards WHERE geometry IS NOT NULL").fetchall()
    for row in rows:
        try:
            geom = json.loads(row["geometry"])
            # _get_coordinates returns a list of linear rings; each ring is a
            # list of [lng, lat] pairs. Average every vertex for an approximate centroid.
            pts = [pt for ring in _get_coordinates(geom) for pt in ring]
            if not pts:
                continue
            lng = sum(p[0] for p in pts) / len(pts)
            lat = sum(p[1] for p in pts) / len(pts)
            out[row["id"]] = (lat, lng)
        except Exception:
            continue

    _WARD_CENTROIDS = out
    return out


def jitter_point(seed: str, lat: float, lng: float) -> tuple:
    """Deterministically offset a point by up to ~±300 m based on `seed` (e.g. a
    complaint id) so that multiple complaints sharing a ward centroid spread out
    into a cluster instead of stacking on one pixel."""
    h = abs(hash(seed))
    dlat = ((h % 1000) / 1000.0 - 0.5) * 0.006
    dlng = (((h // 1000) % 1000) / 1000.0 - 0.5) * 0.006
    return lat + dlat, lng + dlng


def build_heatmap(db: sqlite3.Connection, rows: list) -> list:
    """Build heatmap points from complaint rows. Each row must expose
    `location_lat`, `location_lng`, `status`, `ward_id`, and `complaint_id`.
    Uses explicit GPS coords when present, otherwise falls back to the ward
    centroid (jittered) so every complaint with a known ward gets a dot."""
    centroids = ward_centroids(db)
    points = []
    for r in rows:
        lat, lng = r["location_lat"], r["location_lng"]
        if lat is None or lng is None:
            c = centroids.get(r["ward_id"])
            if not c:
                continue  # ward has no geometry — nothing to place
            lat, lng = jitter_point(r["complaint_id"], c[0], c[1])
        points.append({"lat": lat, "lng": lng, "status": r["status"]})
    return points
