def evaluate_grid_moving_variance(grid: list[list[float]], mean_val: float) -> list[list[float]]:
    rows = len(grid)
    cols = len(grid[0])
    variance_map = [[0.0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            variance_map[r][c] = sum((grid[min(max(0, r + dr), rows - 1)][min(max(0, c + dc), cols - 1)] - mean_val)**2 for dr in (-1, 0, 1) for dc in (-1, 0, 1)) / 9.0
    return variance_map

if __name__ == "__main__":
    g = [[1.0]*3 for _ in range(3)]
    res = evaluate_grid_moving_variance(g, 1.0)
    assert res[1][1] == 0.0
