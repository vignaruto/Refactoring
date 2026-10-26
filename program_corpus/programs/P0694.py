def plus_centres(grid):
    rows, cols = len(grid), len(grid[0])
    centres = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] and grid[r - 1][c] and grid[r + 1][c]:
                if grid[r][c - 1] and grid[r][c + 1]:
                    centres.append((r, c))
    return centres

if __name__ == "__main__":
    plus = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    tee = [[0, 1, 0], [1, 1, 0], [0, 1, 0]]
    assert plus_centres(plus) == [(1, 1)]
    assert plus_centres(tee) == []
