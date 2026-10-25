def joint_grid_histogram(xs: list[float], ys: list[float], bins: int) -> list[list[int]]:
    grid = []
    for _ in range(bins):
        grid.append([0] * bins)
    for r in range(bins):
        for c in range(bins):
            for x, y in zip(xs, ys):
                ix = min(bins - 1, max(0, int(x * bins)))
                iy = min(bins - 1, max(0, int(y * bins)))
                if ix == r and iy == c:
                    grid[r][c] += 1
    return grid

if __name__ == "__main__":
    xs, ys = [0.1, 0.1, 0.9], [0.2, 0.8, 0.9]
    assert joint_grid_histogram(xs, ys, 2) == [[1, 1], [0, 1]]
