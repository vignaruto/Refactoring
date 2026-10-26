def walks_of_length(adj, k):
    n = len(adj)
    counts = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(k):
        nxt = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                nxt[i][j] = sum(counts[i][m] * adj[m][j] for m in range(n))
        counts = nxt
    return counts

if __name__ == "__main__":
    triangle = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    assert walks_of_length(triangle, 2)[0] == [2, 1, 1]
    assert walks_of_length(triangle, 0)[1] == [0, 1, 0]
