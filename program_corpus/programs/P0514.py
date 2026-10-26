def uniform_square_corners(grid: list[list[int]]) -> list[tuple[int, int]]:
    corners = []
    for r in range(len(grid) - 1):
        for c in range(len(grid[0]) - 1):
            v = grid[r][c]
            right, below = grid[r][c + 1], grid[r + 1][c]
            if v != 0 and v == right and v == below and v == grid[r + 1][c + 1]:
                corners.append((r, c))
    return corners

if __name__ == "__main__":
    assert uniform_square_corners([[1, 1, 0], [1, 1, 0], [2, 2, 2]]) == [(0, 0)]
    assert uniform_square_corners([[0, 0], [0, 0]]) == []
