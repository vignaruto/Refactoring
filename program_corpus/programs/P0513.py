def count_vertical_peaks(grid: list[list[int]], minimum: int) -> int:
    rows, cols = len(grid), len(grid[0])
    peaks = 0
    for r in range(rows):
        for c in range(cols):
            value = grid[r][c]
            up = grid[r - 1][c] if r > 0 else -1
            down = grid[r + 1][c] if r < rows - 1 else -1
            if value >= minimum and value > up and value > down:
                peaks += 1
    return peaks

if __name__ == "__main__":
    grid = [[1, 5, 1], [4, 2, 6], [1, 1, 1]]
    assert count_vertical_peaks(grid, 3) == 3
    assert count_vertical_peaks(grid, 9) == 0
