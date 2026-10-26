def plus_shape_centers(grid, value):
    centers = []
    for r in range(1, len(grid) - 1):
        row = grid[r]
        for c in range(1, len(row) - 1):
            col_ok = grid[r - 1][c] == value and grid[r + 1][c] == value
            if row[c] == value and col_ok and row[c - 1] == value and row[c + 1] == value:
                centers.append((r, c))
    return centers

if __name__ == "__main__":
    g = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    assert plus_shape_centers(g, 1) == [(1, 1)]
    assert plus_shape_centers(g, 0) == []
