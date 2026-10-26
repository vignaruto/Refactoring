def count_dag_paths(graph: dict, order: list, source) -> dict:
    ways = {node: 0 for node in order}
    ways[source] = 1
    for node in order:
        for nxt in graph.get(node, []):
            ways[nxt] += ways[node]
    return ways


if __name__ == "__main__":
    graph = {"s": ["a", "b"], "a": ["t"], "b": ["a", "t"]}
    order = ["s", "b", "a", "t"]
    assert count_dag_paths(graph, order, "s")["t"] == 3
