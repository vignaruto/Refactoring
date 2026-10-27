def lu_decomposition_doolittle(
    matrix: list[list[float]]
) -> tuple[list[list[float]], list[list[float]]]:
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    upper = [[0.0] * n for _ in range(n)]
    for i in range(n):
        lower[i][i] = 1.0
        for k in range(i, n):
            sum_u = 0.0
            for j in range(i):
                sum_u += lower[i][j] * upper[j][k]
            upper[i][k] = matrix[i][k] - sum_u
        for k in range(i + 1, n):
            sum_l = 0.0
            for j in range(i):
                sum_l += lower[k][j] * upper[j][i]
            lower[k][i] = (matrix[k][i] - sum_l) / upper[i][i]
    return lower, upper

if __name__ == "__main__":
    m = [[2.0, -1.0], [-4.0, 6.0]]
    l, u = lu_decomposition_doolittle(m)
    assert l[1][0] == -2.0
