def relax_abelian_sandpile(initial: list[list[int]]) -> list[list[int]]:
    size = len(initial)
    grid = [row[:] for row in initial]
    changed = True
    while changed:
        changed = False
        for r in range(size):
            for c in range(size):
                if grid[r][c] >= 4:
                    spill = grid[r][c] // 4
                    grid[r][c] %= 4
                    changed = True
                    if r > 0:
                        grid[r - 1][c] += spill
                    if r + 1 < size:
                        grid[r + 1][c] += spill
                    if c > 0:
                        grid[r][c - 1] += spill
                    if c + 1 < size:
                        grid[r][c + 1] += spill
    return grid

if __name__ == "__main__":
    assert relax_abelian_sandpile([[0, 0, 0], [0, 4, 0], [0, 0, 0]]) == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
