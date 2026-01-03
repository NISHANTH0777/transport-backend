import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

STOP_TO_ROUTES = {}
ROUTE_TO_STOPS = {}


def load_data():
    global STOP_TO_ROUTES, ROUTE_TO_STOPS

    # ---- Load route → stops ----
    with open(DATA_DIR / "route_to_stops.json", "r", encoding="utf-8") as f:
        ROUTE_TO_STOPS = json.load(f)

    # ---- Build stop → routes ----
    STOP_TO_ROUTES = {}

    for route, stops in ROUTE_TO_STOPS.items():
        for stop in stops:
            STOP_TO_ROUTES.setdefault(stop, []).append(route)
