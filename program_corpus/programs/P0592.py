def route_costs(graph, routes):
    totals = []
    for route in routes:
        cost = 0
        for a, b in zip(route, route[1:]):
            cost = cost + graph[a][b]["distance"] * graph[a][b].get("toll_factor", 1.0) + graph[a][b].get("fee", 0)
        totals.append(round(cost, 2))
    return totals

if __name__ == "__main__":
    g = {"a": {}, "b": {}}
    g["a"]["b"] = {"distance": 10}
    g["b"]["c"] = {"distance": 5, "fee": 2}
    assert route_costs(g, [["a", "b", "c"], ["a", "b"]]) == [17.0, 10.0]
