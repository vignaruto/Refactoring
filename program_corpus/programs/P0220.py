def step_porous_diffusion(grid: list[list[float]], coeff: float) -> list[list[float]]:
    h = len(grid)
    w = len(grid[0])
    nxt = [row[:] for row in grid]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            flow = 0.0
            for dr in (-1, 1):
                flow += grid[r + dr][c] - grid[r][c]
            for dc in (-1, 1):
                flow += grid[r][c + dc] - grid[r][c]
            nxt[r][c] += flow * coeff
    return nxt

if __name__ == "__main__":
    m = [[0.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 0.0]]
    res = step_porous_diffusion(m, 0.1)
    assert res[1][1] < 10.0
