def step_wildfire_spread(forest: list[list[int]]) -> list[list[int]]:
    h = len(forest)
    w = len(forest[0])
    nxt = [row[:] for row in forest]
    for r in range(h):
        for c in range(w):
            if forest[r][c] == 1:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < h:
                            if 0 <= nc < w:
                                if forest[nr][nc] == 2:
                                    nxt[r][c] = 2
            elif forest[r][c] == 2:
                nxt[r][c] = 0
    return nxt

if __name__ == "__main__":
    f = [[1, 2], [1, 1]]
    res = step_wildfire_spread(f)
    assert res[0][1] == 0
