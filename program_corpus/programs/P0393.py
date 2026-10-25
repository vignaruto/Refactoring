def brians_brain_step(grid: list[list[int]]) -> list[list[int]]:
    rows, cols = len(grid), len(grid[0])
    nxt = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            state = grid[r][c]
            if state == 1:
                nxt[r][c] = 2
                continue
            if state == 2:
                continue
            firing = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if (dr or dc) and 0 <= rr < rows and 0 <= cc < cols:
                        firing += grid[rr][cc] == 1
            if firing == 2:
                nxt[r][c] = 1
    return nxt

if __name__ == "__main__":
    assert brians_brain_step([[1, 1, 0], [0, 0, 0]]) == [[2, 2, 0], [1, 1, 0]]
