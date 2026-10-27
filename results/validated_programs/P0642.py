def weighted_centrality(edges, nodes):
    strength = {n: 0.0 for n in nodes}
    for u, v, w in edges:
        strength[u] += w
        strength[v] += w
    scores = {}
    for n in nodes:
        neighbours = 0
        for u, v, _ in edges:
            neighbours += (u == n) + (v == n)
        scores[n] = round(strength[n] / max(1, neighbours) * neighbours / max(1, len(nodes) - 1), 3)
    return scores

if __name__ == "__main__":
    edges = [("a", "b", 2.0), ("b", "c", 4.0)]
    scores = weighted_centrality(edges, ["a", "b", "c"])
    assert scores == {"a": 1.0, "b": 3.0, "c": 2.0}
