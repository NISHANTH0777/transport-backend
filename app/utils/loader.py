import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

STOP_TO_ROUTES = load_json("stop_to_routes.json")
ROUTE_TO_STOPS = load_json("route_to_stops.json")
ROUTE_TRANSFERS = load_json("route_transfers.json")
