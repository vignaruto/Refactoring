def game_of_life_step(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid)
    w = len(grid[0])
    nxt = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            neighbors = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < h:
                        if 0 <= nc < w:
                            neighbors += grid[nr][nc]
            is_alive = grid[r][c] == 1
            if is_alive:
                if neighbors in (2, 3):
                    nxt[r][c] = 1
            else:
                if neighbors == 3:
                    nxt[r][c] = 1
    return nxt

if __name__ == "__main__":
    g = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
    res = game_of_life_step(g)
    assert res[1][0] == 1
