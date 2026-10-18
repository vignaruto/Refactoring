def gaussian_elimination_forward(
    matrix: list[list[float]]
) -> list[list[float]]:
    mat = [row[:] for row in matrix]
    n = len(mat)
    for i in range(n):
        pivot = mat[i][i]
        for j in range(i + 1, n):
            factor = mat[j][i] / pivot
            for k in range(i, n + 1):
                mat[j][k] -= factor * mat[i][k]
    return mat

if __name__ == "__main__":
    a = [[2.0, 1.0, 5.0], [4.0, -6.0, -2.0]]
    res = gaussian_elimination_forward(a)
    assert res[1][0] == 0.0
