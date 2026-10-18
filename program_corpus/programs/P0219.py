def compute_pair_reachability_matrix(adj: list[list[int]]) -> list[list[int]]:
    n = len(adj)
    reach = [row[:] for row in adj]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][j] == 0:
                    if reach[i][k] == 1 and reach[k][j] == 1:
                        reach[i][j] = 1
    return reach

if __name__ == "__main__":
    g = [[1, 1, 0], [0, 1, 1], [0, 0, 1]]
    res = compute_pair_reachability_matrix(g)
    assert res[0][2] == 1
