def step_falling_sand(grid: list[list[str]]) -> list[list[str]]:
    rows, cols = len(grid), len(grid[0])
    cells = [row[:] for row in grid]
    for r in range(rows - 2, -1, -1):
        for c in range(cols):
            if cells[r][c] != "s":
                continue
            if cells[r + 1][c] == ".":
                cells[r + 1][c], cells[r][c] = "s", "."
            elif c > 0 and cells[r + 1][c - 1] == "." and cells[r][c - 1] == ".":
                cells[r + 1][c - 1], cells[r][c] = "s", "."
            elif c + 1 < cols and cells[r + 1][c + 1] == "." and cells[r][c + 1] == ".":
                cells[r + 1][c + 1], cells[r][c] = "s", "."
    return cells

if __name__ == "__main__":
    assert step_falling_sand([[".", "s", "."], [".", ".", "."]]) == [[".", ".", "."], [".", "s", "."]]
    assert step_falling_sand([["s", "."], ["s", "."]]) == [[".", "."], ["s", "s"]]
