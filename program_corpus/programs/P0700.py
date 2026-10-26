def equal_corner_rectangles(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0
    for top in range(rows):
        for bottom in range(top + 1, rows):
            for left in range(cols):
                for right in range(left + 1, cols):
                    v = grid[top][left]
                    if v == grid[top][right] and v == grid[bottom][left] and v == grid[bottom][right]:
                        count += 1
    return count

if __name__ == "__main__":
    assert equal_corner_rectangles([[1, 1], [1, 1]]) == 1
    assert equal_corner_rectangles([[1, 1, 1], [1, 1, 1]]) == 3
    assert equal_corner_rectangles([[1, 2], [2, 1]]) == 0
