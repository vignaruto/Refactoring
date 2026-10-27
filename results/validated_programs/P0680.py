def cluster_edge_weights(graph, cluster_of):
    inside = 0.0
    crossing = 0.0
    for node, edges in graph.items():
        for neighbour, weight in edges:
            if cluster_of[node] == cluster_of[neighbour]:
                inside += weight
            else:
                crossing += weight
    cohesion = (inside - crossing) / (inside + crossing) if inside + crossing else 0.0
    return inside / 2, crossing / 2, round(cohesion, 3)

if __name__ == "__main__":
    graph = {"a": [("b", 1)], "c": [("b", 2)]}
    graph["b"] = [("a", 1), ("c", 2)]
    clusters = {"a": 0, "b": 0, "c": 1}
    assert cluster_edge_weights(graph, clusters) == (1.0, 2.0, -0.333)
