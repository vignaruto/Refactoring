def rotate_matrix_clockwise(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    for i in range(n // 2):
        for j in range(i, n - i - 1):
            temp = matrix[i][j]
            matrix[i][j] = matrix[n - 1 - j][i]
            matrix[n - 1 - j][i] = matrix[n - 1 - i][n - 1 - j]
            matrix[n - 1 - i][n - 1 - j] = matrix[j][n - 1 - i]
            matrix[j][n - 1 - i] = temp
    return matrix

if __name__ == "__main__":
    m = [[1, 2], [3, 4]]
    rotate_matrix_clockwise(m)
    assert m == [[3, 1], [4, 2]]
