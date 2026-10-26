def count_triangles(adj: dict) -> int:
    nodes = sorted(adj)
    total = 0
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            for c in adj[a]:
                if b < c and b in adj[a] and c in adj[b]:
                    total += 1
    return total


if __name__ == "__main__":
    adj = {1: {2, 3, 4}, 2: {1, 3}, 3: {1, 2}, 4: {1}}
    assert count_triangles(adj) == 1
    assert count_triangles({1: {2}, 2: {1}}) == 0
