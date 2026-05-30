import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "Samvaad/1.0 (grievance-app)"


def search_places(query: str, region: str = "IND"):
    if not query or not query.strip():
        return []

    try:
        headers = {"User-Agent": USER_AGENT}
        params = {
            "q": query.strip(),
            "format": "json",
            "limit": 8,
            "addressdetails": 1,
        }
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return []

    results = []
    seen = set()
    for place in data:
        lat = place.get("lat")
        lng = place.get("lon")
        name = place.get("name") or ""
        display_name = place.get("display_name") or ""
        full = display_name.strip()
        if lat and lng and full and full not in seen:
            seen.add(full)
            results.append({
                "name": name or full.split(",")[0].strip(),
                "address": full,
                "full": full,
                "lat": float(lat),
                "lng": float(lng),
            })
    return results


def reverse_geocode(lat: float, lng: float) -> dict | None:
    try:
        headers = {"User-Agent": USER_AGENT}
        params = {"lat": lat, "lon": lng, "format": "json", "addressdetails": 1}
        resp = requests.get(NOMINATIM_REVERSE_URL, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {"display_name": data.get("display_name", ""), "address": data.get("address", {})}
    except requests.RequestException:
        return None
