def smooth_interior(grid):
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            edge = grid[r - 1][c] + grid[r + 1][c] + grid[r][c - 1] + grid[r][c + 1]
            out[r][c] = (4 * grid[r][c] + 2 * edge) / 12
    return out

if __name__ == "__main__":
    grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    assert smooth_interior(grid)[1][1] == 2.0
    assert smooth_interior(grid)[0] == [1, 1, 1]
