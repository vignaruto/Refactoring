def count_simple_paths(graph: dict[str, list[str]], src: str, dst: str) -> int:
    total = 0
    stack = [(src, [src])]
    while stack:
        node, path = stack.pop()
        if node == dst:
            total += 1
            continue
        for nxt in graph.get(node, []):
            if nxt not in path:
                stack.append((nxt, path + [nxt]))
    return total

if __name__ == "__main__":
    graph = {"a": ["b", "c"], "b": ["c", "d"], "c": ["d"]}
    assert count_simple_paths(graph, "a", "d") == 3
