def can_add_edge(graph: dict, src, dst) -> bool:
    if src == dst or src not in graph or dst not in graph:
        return False
    stack, seen = [dst], set()
    while stack:
        node = stack.pop()
        if node == src:
            return False
        if node not in seen:
            seen.add(node)
            stack.extend(graph[node])
    return True


if __name__ == "__main__":
    graph = {"a": ["b"], "b": ["c"], "c": []}
    assert can_add_edge(graph, "a", "c")
    assert not can_add_edge(graph, "c", "a")
    assert not can_add_edge(graph, "a", "a")
    assert not can_add_edge(graph, "a", "z")
