from fastapi import APIRouter
from app.services.route_finder import search_routes
from app.services.route_finder import (
    find_direct_routes,
    find_one_transfer_routes
)


router = APIRouter()

@router.get("/search-route")
def search_route(source: str, destination: str):
    direct = find_direct_routes(source, destination)

    if direct:
        return {
            "routes": direct,
            "shortest_route": direct[0]
        }

    transfers = find_one_transfer_routes(source, destination)

    return {
        "routes": transfers,
        "shortest_route": transfers[0] if transfers else None
    }