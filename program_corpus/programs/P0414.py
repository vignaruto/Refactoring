def graph_density_metrics(node_count: int, edges: list[tuple[int, int]]) -> tuple[float, float]:
    if node_count < 2:
        raise ValueError("need at least two nodes")
    unique_edges = {(min(u, v), max(u, v)) for u, v in edges if u != v}
    density = 2.0 * len(unique_edges) / (node_count * (node_count - 1))
    average_degree = 2.0 * len(unique_edges) / node_count
    return round(density, 4), round(average_degree, 4)

if __name__ == "__main__":
    assert graph_density_metrics(4, [(0, 1), (1, 0), (1, 2), (2, 2)]) == (0.3333, 1.0)
