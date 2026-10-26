def within_hops(graph, start, k, blocked):
    frontier = [start]
    seen = {start}
    for _ in range(k):
        nxt = []
        for node in frontier:
            for nbr in graph.get(node, []):
                if nbr not in seen and nbr not in blocked and nbr in graph:
                    seen.add(nbr)
                    nxt.append(nbr)
        frontier = nxt
    return sorted(seen - {start})

if __name__ == "__main__":
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d", "x"]}
    graph["d"] = ["e"]
    graph["e"] = []
    assert within_hops(graph, "a", 2, {"c"}) == ["b", "d"]
    assert within_hops(graph, "a", 3, set()) == ["b", "c", "d", "e"]
