import itertools

def topple_sandpile(grid):
    cells = [row[:] for row in grid]
    rows, cols = len(cells), len(cells[0])
    rounds = 0
    changed = True
    while changed:
        changed = False
        for r, c in itertools.product(range(rows), range(cols)):
            if cells[r][c] < 4:
                continue
            changed = True
            cells[r][c] -= 4
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                condition = 0 <= nr < rows and 0 <= nc < cols
                if condition:
                    cells[nr][nc] += 1
        rounds += 1
    return cells, rounds

if __name__ == "__main__":
    grid = [[0, 0, 0], [0, 4, 0], [0, 0, 0]]
    cells, rounds = topple_sandpile(grid)
    assert cells == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    assert rounds == 2
