import heapq

def dijkstra_distances(graph: dict[str, list[tuple[str, float]]], source: str) -> dict[str, float]:
    best = {source: 0.0}
    heap = [(0.0, source)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > best.get(node, float("inf")):
            continue
        for neighbor, weight in graph.get(node, []):
            candidate = dist + weight
            if candidate < best.get(neighbor, float("inf")):
                best[neighbor] = candidate
                heapq.heappush(heap, (candidate, neighbor))
    return best

if __name__ == "__main__":
    g = {"a": [("b", 4.0), ("c", 1.0)], "c": [("b", 2.0)]}
    assert dijkstra_distances(g, "a") == {"a": 0.0, "b": 3.0, "c": 1.0}
