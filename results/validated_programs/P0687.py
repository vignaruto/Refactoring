def local_peaks(grid, min_height):
    rows, cols = len(grid), len(grid[0])
    peaks = []
    for r in range(rows):
        row = grid[r]
        for c in range(cols):
            h = row[c]
            up = grid[r - 1][c] if r > 0 else -1
            down = grid[r + 1][c] if r < rows - 1 else -1
            left = row[c - 1] if c > 0 else -1
            right = row[c + 1] if c < cols - 1 else -1
            condition = h >= min_height and h > max(up, down)
            if condition:
                condition = h > max(left, right)
            if condition:
                score = (h - max(up, down, left, right, 0)) * 2
                score = score + (h - min_height) / max(h, 1)
                peaks.append((r, c, round(score, 2)))
    return peaks

if __name__ == "__main__":
    grid = [[1, 2, 1], [2, 9, 2], [1, 2, 1]]
    assert local_peaks(grid, 5) == [(1, 1, 14.44)]
    assert local_peaks(grid, 10) == []
