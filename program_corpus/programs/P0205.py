def is_toeplitz_matrix(matrix: list[list[int]]) -> bool:
    rows = len(matrix)
    cols = len(matrix[0])
    flat_len = (rows - 1) * (cols - 1)
    for k in range(flat_len):
        r = k // (cols - 1)
        c = k % (cols - 1)
        if matrix[r][c] != matrix[r + 1][c + 1]:
            return False
    return True

if __name__ == "__main__":
    m = [[1, 2, 3, 4], [5, 1, 2, 3], [9, 5, 1, 2]]
    assert is_toeplitz_matrix(m) is True
