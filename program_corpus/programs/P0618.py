def hill_climb_peaks(grid, starts):
    peaks = []
    for r, c in starts:
        moved = True
        while moved:
            moved = False
            best = grid[r][c]
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] > best:
                    best, r, c, moved = grid[nr][nc], nr, nc, True
        peaks.append((r, c))
    return peaks

if __name__ == "__main__":
    grid = [[1, 2, 3], [2, 3, 4], [3, 4, 9]]
    assert hill_climb_peaks(grid, [(0, 0), (2, 2)]) == [(2, 2), (2, 2)]
