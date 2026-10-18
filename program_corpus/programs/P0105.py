def is_matrix_symmetric(matrix: list[list[float]]) -> bool:
    n = len(matrix)
    flat_len = n * n
    for k in range(flat_len):
        r = k // n
        c = k % n
        if matrix[r][c] != matrix[c][r]:
            return False
    return True

if __name__ == "__main__":
    mat = [[1.0, 2.0], [2.0, 1.0]]
    assert is_matrix_symmetric(mat) is True
