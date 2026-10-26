def evaluate_route(path: list[str], weights: dict[tuple[str, str], float], closed: set[str], budget: float) -> float:
    legs = list(zip(path, path[1:]))
    total_cost = sum(weights.get(leg, weights.get((leg[1], leg[0]), float("inf"))) for leg in legs)
    if len(path) < 2 or total_cost > budget or closed.intersection(path):
        return -1.0
    return round(total_cost, 2)

if __name__ == "__main__":
    roads = {("a", "b"): 2.0, ("c", "b"): 3.5}
    assert evaluate_route(["a", "b", "c"], roads, set(), 10.0) == 5.5
    assert evaluate_route(["a", "b", "c"], roads, {"b"}, 10.0) == -1.0
