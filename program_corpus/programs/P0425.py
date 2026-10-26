def can_add_dependency(graph: dict[str, set[str]], src: str, dst: str) -> bool:
    if src == dst or src not in graph or dst not in graph:
        return False
    stack = [dst]
    seen = set()
    while stack:
        node = stack.pop()
        if node == src:
            return False
        seen.add(node)
        stack.extend(n for n in graph[node] if n not in seen)
    return True

if __name__ == "__main__":
    deps = {"a": {"b"}, "b": {"c"}, "c": set()}
    assert can_add_dependency(deps, "c", "a") is False
    assert can_add_dependency(deps, "a", "c") is True
