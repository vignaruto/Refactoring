def coastline_cells(grid):
    rows, cols = len(grid), len(grid[0])
    coast = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1:
                continue
            edge = r == 0 or c == 0 or r == rows - 1 or c == cols - 1
            if edge or grid[r - 1][c] == 0 or grid[r + 1][c] == 0 or grid[r][c - 1] == 0 or grid[r][c + 1] == 0:
                coast += 1
    return coast

if __name__ == "__main__":
    island = [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0]]
    island.append([0, 0, 0, 0])
    assert coastline_cells(island) == 4
    assert coastline_cells([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) == 8
