def cross_correlation_matrix(matrix_x: list[list[float]], matrix_y: list[list[float]]) -> list[list[float]]:
    m = len(matrix_x)
    n = len(matrix_y)
    corr_table = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            corr_table[i][j] = sum(matrix_x[i][k] * matrix_y[j][k] for k in range(len(matrix_x[i]))) / ((sum(v**2 for v in matrix_x[i])**0.5) * (sum(v**2 for v in matrix_y[j])**0.5) + 1e-9)
    return corr_table

if __name__ == "__main__":
    a = [[1.0, 2.0]]
    b = [[2.0, 4.0]]
    res = cross_correlation_matrix(a, b)
    assert round(res[0][0], 2) == 1.0
