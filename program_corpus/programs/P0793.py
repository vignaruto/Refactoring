import heapq

def constrained_mst(graph, start, forbidden, max_weight):
    visited = {start}
    heap = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)
    edges = []
    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in visited or (u, v) in forbidden or (v, u) in forbidden or w > max_weight:
            continue
        visited.add(v)
        edges.append((u, v, w))
        for nxt, nw in graph[v]:
            if nxt not in visited:
                heapq.heappush(heap, (nw, v, nxt))
    mean_weight = sum(w for _, _, w in edges) / max(len(edges), 1)
    complete = len(visited) == len(graph)
    return edges, round(mean_weight, 2), complete

if __name__ == "__main__":
    graph = {"a": [("b", 1), ("c", 4)]}
    graph["b"] = [("a", 1), ("c", 2)]
    graph["c"] = [("a", 4), ("b", 2)]
    edges, mean, done = constrained_mst(graph, "a", set(), 10)
    assert (edges, mean, done) == ([("a", "b", 1), ("b", "c", 2)], 1.5, True)
    assert constrained_mst(graph, "a", {("b", "c")}, 10)[1] == 2.5
    assert constrained_mst(graph, "a", set(), 1)[2] is False
