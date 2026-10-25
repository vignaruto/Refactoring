def uf_find_root(parent: dict[str, str], node: str) -> str:
    while parent[node] != node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node

def count_union_components(nodes: list[str], edges: list[tuple[str, str]]) -> int:
    parent = {node: node for node in nodes}
    for a, b in edges:
        root_a = uf_find_root(parent, a)
        root_b = uf_find_root(parent, b)
        if root_a != root_b:
            parent[root_a] = root_b
    return len({uf_find_root(parent, n) for n in nodes})

if __name__ == "__main__":
    assert count_union_components(["a", "b", "c", "d"], [("a", "b"), ("c", "d")]) == 2
    assert count_union_components(["x"], []) == 1
