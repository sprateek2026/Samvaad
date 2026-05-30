from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from ..database import get_db
from ..services.gis_service import locate_ward
from ..services.mapmyindia import search_places, reverse_geocode

router = APIRouter()


class LocateRequest(BaseModel):
    latitude: float
    longitude: float


class PincodeRequest(BaseModel):
    pin_code: str


@router.post("/locate")
def locate(req: LocateRequest, db: sqlite3.Connection = Depends(get_db)):
    ward = locate_ward(req.latitude, req.longitude, db)
    if not ward:
        raise HTTPException(status_code=404, detail="No ward found for this location")
    return ward


@router.post("/pincode-lookup")
def pincode_lookup(req: PincodeRequest, db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        """SELECT w.id, w.ward_number, w.ward_name, w.ward_name_mr,
                  w.corporator_a_name, w.mla_name, w.mp_name,
                  pw.locality
           FROM pincode_ward_mapping pw
           JOIN wards w ON pw.ward_id = w.id
           WHERE pw.pin_code = ?""",
        (req.pin_code,)
    ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No wards found for this PIN code")
    return {"wards": [dict(r) for r in rows]}


@router.get("/autocomplete")
def autocomplete(q: str = Query(..., min_length=2)):
    results = search_places(q)
    return {"suggestions": results}


@router.get("/reverse-geocode")
def get_reverse_geocode(lat: float = Query(...), lng: float = Query(...)):
    result = reverse_geocode(lat, lng)
    if not result:
        raise HTTPException(status_code=404, detail="Reverse geocode failed")
    return result


@router.get("/localities")
def get_localities(pin_code: str, db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        """SELECT l.id, l.name, w.id as ward_id, w.ward_number, w.ward_name
           FROM localities l JOIN wards w ON l.ward_id = w.id
           WHERE l.pin_code = ?
           ORDER BY l.name""",
        (pin_code,)
    ).fetchall()
    return {"localities": [dict(r) for r in rows]}


@router.get("/wards")
def list_wards(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT id, ward_number, ward_name, corporator_a_name FROM wards ORDER BY ward_number"
    ).fetchall()
    return {"wards": [dict(r) for r in rows]}
