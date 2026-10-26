def anti_diagonals(grid):
    rows, cols = len(grid), len(grid[0])
    diagonals = [[] for _ in range(rows + cols - 1)]
    for r in range(rows):
        for c in range(cols):
            diagonals[r + c].append(grid[r][c])
    return diagonals

def heaviest_diagonal(grid):
    sums = [sum(d) for d in anti_diagonals(grid)]
    return sums.index(max(sums))

if __name__ == "__main__":
    grid = [[1, 2, 3], [4, 5, 6]]
    assert anti_diagonals(grid) == [[1], [2, 4], [3, 5], [6]]
    assert heaviest_diagonal(grid) == 2
