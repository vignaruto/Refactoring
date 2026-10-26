import heapq

def cheapest_route(graph, start, goal, banned, tolls, max_hops, surcharge=0.0, toll_fee=5):
    best = {start: 0}
    heap = [(0, 0, start)]
    while heap:
        dist, hops, node = heapq.heappop(heap)
        if node == goal:
            return dist
        if dist > best.get(node, float("inf")):
            continue
        for nxt, weight in graph.get(node, []):
            cost = dist + weight * (1 + surcharge) + toll_fee * (nxt in tolls)
            if nxt in banned or hops >= max_hops or cost >= best.get(nxt, float("inf")):
                continue
            best[nxt] = cost
            heapq.heappush(heap, (cost, hops + 1, nxt))
    return None

if __name__ == "__main__":
    graph = {"a": [("b", 1), ("c", 4)]}
    graph["b"] = [("c", 1), ("d", 5)]
    graph["c"] = [("d", 1)]
    assert cheapest_route(graph, "a", "d", set(), set(), 5) == 3
    assert cheapest_route(graph, "a", "d", {"c"}, set(), 5) == 6
    assert cheapest_route(graph, "a", "d", set(), {"c"}, 5) == 6
    assert cheapest_route(graph, "a", "d", set(), set(), 1) is None
