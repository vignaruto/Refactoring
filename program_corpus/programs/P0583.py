def press_lights(grid, presses):
    rows, cols = len(grid), len(grid[0])
    state = [row[:] for row in grid]
    for r, c in presses:
        for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                state[nr][nc] = 1 - state[nr][nc]
    return state

if __name__ == "__main__":
    dark = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert press_lights(dark, [(1, 1)]) == [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    assert press_lights(dark, [(0, 0)]) == [[1, 1, 0], [1, 0, 0], [0, 0, 0]]
