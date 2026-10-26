def saddle_points(matrix: list[list[int]]) -> list[tuple[int, int]]:
    col_mins = [min(col) for col in zip(*matrix)]
    points = []
    for r, row in enumerate(matrix):
        row_max = max(row)
        for c, value in enumerate(row):
            if value == row_max and value == col_mins[c]:
                points.append((r, c))
    return points


if __name__ == "__main__":
    matrix = [[9, 8, 7], [5, 3, 2], [6, 6, 7]]
    assert saddle_points(matrix) == [(1, 0)]
