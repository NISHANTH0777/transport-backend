import json
from collections import defaultdict, deque

# -------------------------------------------------
# Load data ONCE
# -------------------------------------------------
with open("data/stop_to_routes.json", "r", encoding="utf-8") as f:
    STOP_TO_ROUTES = json.load(f)

with open("data/route_to_stops.json", "r", encoding="utf-8") as f:
    ROUTE_TO_STOPS = json.load(f)


# -------------------------------------------------
# Utility: Fare calculation (simple & academic)
# -------------------------------------------------
def calculate_fare(stop_count: int) -> int:
    return max(10, (stop_count // 3) * 5)


# -------------------------------------------------
# 1️⃣ DIRECT ROUTES
# -------------------------------------------------
def find_direct_routes(source: str, destination: str):
    results = []

    src_routes = set(STOP_TO_ROUTES.get(source, []))
    dst_routes = set(STOP_TO_ROUTES.get(destination, []))

    for route in src_routes & dst_routes:
        stops = ROUTE_TO_STOPS.get(route, [])

        if source in stops and destination in stops:
            i = stops.index(source)
            j = stops.index(destination)

            if i < j:
                segment = stops[i:j + 1]
            elif i > j:
                segment = list(reversed(stops[j:i + 1]))
            else:
                continue

            results.append({
                "type": "direct",
                "bus_number": route,
                "stops": segment,
                "stop_count": len(segment),
                "fare": calculate_fare(len(segment))
            })

    return sorted(results, key=lambda r: r["stop_count"])

def find_one_transfer_routes(source: str, destination: str):
    results = []

    # Routes starting from source
    source_routes = STOP_TO_ROUTES.get(source, [])

    # Routes ending at destination
    destination_routes = STOP_TO_ROUTES.get(destination, [])

    for r1 in source_routes:
        stops_r1 = ROUTE_TO_STOPS.get(r1, [])

        for r2 in destination_routes:
            if r1 == r2:
                continue

            stops_r2 = ROUTE_TO_STOPS.get(r2, [])

            # Find common transfer stops
            common_stops = set(stops_r1) & set(stops_r2)

            for transfer in common_stops:
                try:
                    i1 = stops_r1.index(source)
                    t1 = stops_r1.index(transfer)

                    t2 = stops_r2.index(transfer)
                    j2 = stops_r2.index(destination)
                except ValueError:
                    continue

                # Direction check (forward OR reverse)
                if i1 < t1 and t2 < j2:
                    segment1 = stops_r1[i1:t1 + 1]
                    segment2 = stops_r2[t2:j2 + 1]
                elif i1 > t1 and t2 > j2:
                    segment1 = stops_r1[t1:i1 + 1][::-1]
                    segment2 = stops_r2[j2:t2 + 1][::-1]
                else:
                    continue

                full_path = segment1 + segment2[1:]

                results.append({
                    "type": "1-transfer",
                    "routes": [r1, r2],
                    "transfer_at": transfer,
                    "from": source,
                    "to": destination,
                    "stops": full_path,
                    "stop_count": len(full_path),
                    "fare": calculate_fare(len(full_path))
                })

    results.sort(key=lambda r: r["stop_count"])
    return results


# -------------------------------------------------
# 2️⃣ ONE-TRANSFER ROUTES
# -------------------------------------------------
def find_connected_routes(source: str, destination: str):
    results = []

    source_buses = STOP_TO_ROUTES.get(source, [])
    dest_buses = STOP_TO_ROUTES.get(destination, [])

    for bus1 in source_buses:
        stops1 = ROUTE_TO_STOPS.get(bus1, [])

        if source not in stops1:
            continue

        for bus2 in dest_buses:
            if bus1 == bus2:
                continue

            stops2 = ROUTE_TO_STOPS.get(bus2, [])

            if destination not in stops2:
                continue

            # 🔁 Find transfer stop
            common_stops = set(stops1) & set(stops2)

            for transfer in common_stops:
                i1 = stops1.index(source)
                t1 = stops1.index(transfer)

                i2 = stops2.index(destination)
                t2 = stops2.index(transfer)

                # Segment 1
                if i1 < t1:
                    seg1 = stops1[i1:t1 + 1]
                else:
                    seg1 = list(reversed(stops1[t1:i1 + 1]))

                # Segment 2
                if t2 < i2:
                    seg2 = stops2[t2:i2 + 1]
                else:
                    seg2 = list(reversed(stops2[i2:t2 + 1]))

                total_stops = len(seg1) + len(seg2) - 1

                results.append({
                    "type": "transfer",
                    "bus_1": bus1,
                    "bus_2": bus2,
                    "transfer_stop": transfer,
                    "stops_1": seg1,
                    "stops_2": seg2,
                    "stop_count": total_stops,
                    "fare": calculate_fare(total_stops)
                })

    return sorted(results, key=lambda r: r["stop_count"])
# -------------------------------------------------
# 3️⃣ BUILD STOP GRAPH (FOR BFS)
# -------------------------------------------------
STOP_GRAPH = defaultdict(list)

def build_stop_graph():
    for route, stops in ROUTE_TO_STOPS.items():
        for i in range(len(stops) - 1):
            STOP_GRAPH[stops[i]].append({
                "next": stops[i + 1],
                "route": route
            })

build_stop_graph()


# -------------------------------------------------
# 4️⃣ BFS FOR ALL-STATION ROUTING
# -------------------------------------------------
def bfs_route(source: str, destination: str):
    queue = deque()
    queue.append((source, [], []))
    visited = set()

    while queue:
        stop, path, routes = queue.popleft()

        if stop == destination:
            return path + [stop], routes

        if stop in visited:
            continue
        visited.add(stop)

        for edge in STOP_GRAPH.get(stop, []):
            queue.append((
                edge["next"],
                path + [stop],
                routes + [edge["route"]]
            ))

    return None, None


def bfs_to_segments(stops, routes):
    segments = []
    start = stops[0]
    current_route = routes[0]

    for i in range(1, len(stops)):
        if routes[i - 1] != current_route:
            segments.append({
                "bus_number": current_route,
                "from": start,
                "to": stops[i - 1]
            })
            start = stops[i - 1]
            current_route = routes[i - 1]

    segments.append({
        "bus_number": current_route,
        "from": start,
        "to": stops[-1]
    })

    return segments


# -------------------------------------------------
# 5️⃣ MASTER SEARCH FUNCTION (HYBRID)
# -------------------------------------------------
def search_routes(source: str, destination: str):
    all_routes = []

    # 1️⃣ Direct routes
    direct = find_direct_routes(source, destination)
    for r in direct:
        r["category"] = "direct"
        r["total_stops"] = r["stop_count"]
        all_routes.append(r)

    # 2️⃣ One-transfer routes
    transfers = find_one_transfer_routes(source, destination)
    for r in transfers:
        r["category"] = "transfer"
        all_routes.append(r)

    # 3️⃣ BFS multi-transfer route
    stops, routes = bfs_route(source, destination)
    if stops:
        bfs_route_obj = {
            "type": "multi_transfer",
            "category": "bfs",
            "path": stops,
            "segments": bfs_to_segments(stops, routes),
            "total_stops": len(stops),
            "fare": calculate_fare(len(stops))
        }
        all_routes.append(bfs_route_obj)

    # ❌ No route at all
    if not all_routes:
        return {
            "routes": [],
            "shortest_route": None
        }

    # 4️⃣ Sort ALL routes by least stops
    all_routes.sort(key=lambda r: r.get("total_stops", 999))

    # 5️⃣ Mark shortest route
    all_routes[0]["is_shortest"] = True
    for r in all_routes[1:]:
        r["is_shortest"] = False

    return {
        "routes": all_routes,
        "shortest_route": all_routes[0]
    }
