import math

def cholesky_decomposition(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            sum_k = 0.0
            for k in range(j):
                sum_k += lower[i][k] * lower[j][k]
            if i == j:
                lower[i][j] = math.sqrt(max(0.0, matrix[i][i] - sum_k))
            else:
                lower[i][j] = (matrix[i][j] - sum_k) / lower[j][j]
    return lower

if __name__ == "__main__":
    m = [[4.0, 12.0], [12.0, 37.0]]
    l = cholesky_decomposition(m)
    assert l[0][0] == 2.0
