def aggregate_route_emissions(routes: dict[str, list[dict[str, float]]], grid_kg_per_kwh: float) -> dict[str, float]:
    totals = {}
    for route_name, legs in routes.items():
        route_total = 0.0
        for leg in legs:
            diesel_kg = leg["distance_km"] * leg.get("diesel_l_per_km", 0.0) * 2.68 * (1.0 + 0.1 * leg.get("payload_t", 0.0) / max(1.0, leg.get("capacity_t", 1.0)))
            electric_kg = leg["distance_km"] * leg.get("kwh_per_km", 0.0) * grid_kg_per_kwh
            route_total += diesel_kg + electric_kg
        totals[route_name] = round(route_total, 3)
    return totals

if __name__ == "__main__":
    assert aggregate_route_emissions({"A": [{"distance_km": 100.0, "diesel_l_per_km": 0.3, "capacity_t": 10.0}], "B": [{"distance_km": 50.0, "kwh_per_km": 1.2}]}, 0.5) == {"A": 80.4, "B": 30.0}
