def count_magic_squares(grid: list[list[int]]) -> int:
    found = 0
    for r in range(len(grid) - 2):
        for c in range(len(grid[0]) - 2):
            block = [row[c:c + 3] for row in grid[r:r + 3]]
            values = sorted(v for row in block for v in row)
            rows_ok = all(sum(row) == 15 for row in block)
            cols_ok = all(sum(col) == 15 for col in zip(*block))
            diag = block[0][0] + block[1][1] + block[2][2]
            if values == list(range(1, 10)) and rows_ok and cols_ok and diag == 15:
                found += 1
    return found

if __name__ == "__main__":
    grid = [[4, 3, 8, 4], [9, 5, 1, 9], [2, 7, 6, 2]]
    assert count_magic_squares(grid) == 1
