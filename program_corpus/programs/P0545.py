def bellman_ford_costs(edges: list[tuple[str, str, int]], nodes: list[str], source: str) -> dict[str, float]:
    cost = {n: float("inf") for n in nodes}
    cost[source] = 0
    for _ in range(len(nodes) - 1):
        for u, v, w in edges:
            if cost[u] != float("inf") and cost[u] + w < cost[v] and v != source:
                cost[v] = cost[u] + w
    for u, v, w in edges:
        candidate_cost_through_edge = cost[u] + w if cost[u] != float("inf") else float("inf")
        if candidate_cost_through_edge < cost[v]:
            raise ValueError("negative cycle")
    return cost

if __name__ == "__main__":
    edges = [("a", "b", 4), ("a", "c", 1), ("c", "b", 2)]
    edges.append(("b", "d", 1))
    costs = bellman_ford_costs(edges, ["a", "b", "c", "d"], "a")
    assert costs == {"a": 0, "b": 3, "c": 1, "d": 4}
