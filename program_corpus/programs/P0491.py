def bridge_edges(nodes: list[str], edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    bridges = []
    for removed in edges:
        remaining = [e for e in edges if e != removed]
        seen = {nodes[0]}
        stack = [nodes[0]]
        while stack:
            node = stack.pop()
            for u, v in remaining:
                other = v if u == node else u
                if node in (u, v) and other not in seen and u != v:
                    seen.add(other)
                    stack.append(other)
        if len(seen) < len(nodes):
            bridges.append(removed)
    return bridges

if __name__ == "__main__":
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")]
    assert bridge_edges(["a", "b", "c", "d"], edges) == [("c", "d")]
