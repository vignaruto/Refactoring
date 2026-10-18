def compute_dispatch_freight_penalties(hubs: list[dict[str, float]], destinations: list[dict[str, float]]) -> list[list[float]]:
    cost_matrix = []
    for hub in hubs:
        row = []
        for dst in destinations:
            transit_cost = (hub["base_fee"] * 1.05) + (((hub["x"] - dst["x"])**2 + (hub["y"] - dst["y"])**2)**0.5 * hub["per_km_rate"] * (1.0 + dst.get("congestion_index", 0.1))) + (dst["weight_kg"] * 0.45)
            row.append(transit_cost)
        cost_matrix.append(row)
    return cost_matrix

if __name__ == "__main__":
    h = [{"base_fee": 50.0, "x": 0.0, "y": 0.0, "per_km_rate": 1.2}]
    d = [{"x": 3.0, "y": 4.0, "congestion_index": 0.2, "weight_kg": 10.0}]
    assert len(compute_dispatch_freight_penalties(h, d)) == 1
