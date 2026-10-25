from collections import deque

def kahn_topological_order(graph: dict[str, list[str]]) -> list[str]:
    in_degree = {u: 0 for u in graph}
    for u, neighbors in graph.items():
        for v in neighbors:
            in_degree[v] = in_degree.get(v, 0) + 1
    zero_nodes = [u for u, d in in_degree.items() if d == 0]
    ready = deque(sorted(zero_nodes))
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                ready.append(nxt)
    return order

if __name__ == "__main__":
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    assert kahn_topological_order(g) == ["a", "b", "c", "d"]
