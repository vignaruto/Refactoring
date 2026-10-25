def find_axial_extrema(grid: list[list[float]]) -> list[tuple[int, int, str]]:
    rows, cols = len(grid), len(grid[0])
    extrema = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            val = grid[r][c]
            up, down = grid[r - 1][c], grid[r + 1][c]
            left, right = grid[r][c - 1], grid[r][c + 1]
            if val > up and val > down and val > left and val > right:
                extrema.append((r, c, "peak"))
            elif val < up and val < down and val < left and val < right:
                extrema.append((r, c, "pit"))
    return extrema

if __name__ == "__main__":
    assert find_axial_extrema([[1, 2, 1], [2, 9, 2], [1, 2, 1]]) == [(1, 1, "peak")]
    assert find_axial_extrema([[5, 4, 5], [4, 0, 4], [5, 4, 5]]) == [(1, 1, "pit")]
