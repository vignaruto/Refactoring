def count_triad_cliques(adj: list[list[int]]) -> int:
    n = len(adj)
    cliques = 0
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u][v] == 1:
                for w in range(v + 1, n):
                    if adj[v][w] == 1:
                        if adj[u][w] == 1:
                            cliques += 1
    return cliques

if __name__ == "__main__":
    g = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    assert count_triad_cliques(g) == 1
