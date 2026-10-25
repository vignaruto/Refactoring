def langtons_ant_black_cells(size: int, steps: int) -> int:
    grid = [[0] * size for _ in range(size)]
    row, col = size // 2, size // 2
    heading = 0
    moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    for _ in range(steps):
        if grid[row][col] == 0:
            heading = (heading + 1) % 4
        else:
            heading = (heading - 1) % 4
        grid[row][col] ^= 1
        dr, dc = moves[heading]
        row = (row + dr) % size
        col = (col + dc) % size
    black = 0
    for line in grid:
        for cell in line:
            black += cell
    return black

if __name__ == "__main__":
    assert langtons_ant_black_cells(5, 0) == 0
    assert langtons_ant_black_cells(5, 4) == 4
