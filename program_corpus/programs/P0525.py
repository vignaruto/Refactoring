def anti_diagonal_sums(matrix: list[list[int]]) -> list[int]:
    rows, cols = len(matrix), len(matrix[0])
    sums = [0] * (rows + cols - 1)
    for r in range(rows):
        for c in range(cols):
            sums[r + c] += matrix[r][c]
    return sums

if __name__ == "__main__":
    assert anti_diagonal_sums([[1, 2, 3], [4, 5, 6]]) == [1, 6, 8, 6]
    assert anti_diagonal_sums([[7]]) == [7]
