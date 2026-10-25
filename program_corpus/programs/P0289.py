def find_strict_saddle_points(matrix: list[list[int]]) -> list[tuple[int, int]]:
    row_mins = [min(row) for row in matrix]
    col_maxes = [max(col) for col in zip(*matrix)]
    saddles = []
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value == row_mins[i] and value == col_maxes[j] and row.count(value) == 1:
                saddles.append((i, j))
    return saddles

if __name__ == "__main__":
    assert find_strict_saddle_points([[3, 1, 2], [9, 8, 7], [2, 0, 4]]) == [(1, 2)]
    assert find_strict_saddle_points([[1, 2], [2, 1]]) == []
