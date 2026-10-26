def prefix_table(grid):
    rows, cols = len(grid), len(grid[0])
    table = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            above = table[r][c + 1]
            left = table[r + 1][c]
            corner = table[r][c]
            table[r + 1][c + 1] = grid[r][c] + above + left - corner
    return table

def block_sum(t, r1, c1, r2, c2):
    return t[r2][c2] - t[r1][c2] - t[r2][c1] + t[r1][c1]

if __name__ == "__main__":
    t = prefix_table([[1, 2], [3, 4]])
    assert t[2][2] == 10
    assert block_sum(t, 1, 0, 2, 2) == 7
    assert block_sum(t, 0, 1, 2, 2) == 6
