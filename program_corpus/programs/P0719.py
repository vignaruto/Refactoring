def convolve_2x2(grid, k):
    out = []
    for r in range(len(grid) - 1):
        row = []
        for c in range(len(grid[0]) - 1):
            value = grid[r][c] * k[0][0] + grid[r][c + 1] * k[0][1] + grid[r + 1][c] * k[1][0] + grid[r + 1][c + 1] * k[1][1]
            row.append(value)
        out.append(row)
    return out

if __name__ == "__main__":
    grid = [[1, 2, 3], [4, 5, 6]]
    assert convolve_2x2(grid, [[1, 0], [0, -1]]) == [[-4, -4]]
    assert convolve_2x2(grid, [[1, 1], [1, 1]]) == [[12, 16]]
