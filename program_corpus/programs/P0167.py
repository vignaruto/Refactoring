def is_valid_sudoku_grid(board: list[list[int]]) -> bool:
    for i in range(9):
        row_seen = set()
        for j in range(9):
            val = board[i][j]
            if val != 0:
                if val in row_seen:
                    return False
                row_seen.add(val)
    for j in range(9):
        col_seen = set()
        for i in range(9):
            val = board[i][j]
            if val != 0:
                if val in col_seen:
                    return False
                col_seen.add(val)
    return True

if __name__ == "__main__":
    b = [[0]*9 for _ in range(9)]
    b[0][0] = 5
    b[0][1] = 3
    assert is_valid_sudoku_grid(b) is True
