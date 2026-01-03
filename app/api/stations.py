from fastapi import APIRouter, Query
from app.utils.loader import STOP_TO_ROUTES

router = APIRouter()

STATIONS = sorted(STOP_TO_ROUTES.keys())

@router.get("/stations/search")
def search_stations(q: str = Query(..., min_length=1)):
    q = q.lower()
    return [s for s in STATIONS if q in s.lower()][:10]
