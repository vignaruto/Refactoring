def compute_integral_image(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid)
    w = len(grid[0])
    integral = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            top = integral[r - 1][c] if r > 0 else 0
            left = integral[r][c - 1] if c > 0 else 0
            diag = integral[r - 1][c - 1] if r > 0 and c > 0 else 0
            integral[r][c] = val + top + left - diag
    return integral

if __name__ == "__main__":
    g = [[1, 2], [3, 4]]
    res = compute_integral_image(g)
    assert res[1][1] == 10
