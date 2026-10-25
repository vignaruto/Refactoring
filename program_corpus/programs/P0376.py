ROWS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
COLS = ((0, 3, 6), (1, 4, 7), (2, 5, 8))
DIAGS = ((0, 4, 8), (2, 4, 6))

def count_wins(board: str, mark: str) -> int:
    wins = 0
    for a, b, c in ROWS + COLS + DIAGS:
        if board[a] == mark and board[b] == mark and board[c] == mark:
            wins += 1
    return wins

def is_reachable_tictactoe(board: str) -> bool:
    x_count = board.count("X")
    o_count = board.count("O")
    if len(board) != 9 or x_count < o_count or x_count > o_count + 1:
        return False
    x_wins = count_wins(board, "X")
    o_wins = count_wins(board, "O")
    if x_wins and o_wins:
        return False
    if x_wins and x_count != o_count + 1:
        return False
    if o_wins and x_count != o_count:
        return False
    return True

if __name__ == "__main__":
    assert is_reachable_tictactoe("XXXOO....") is True
    assert is_reachable_tictactoe("XXXOOO...") is False
    assert is_reachable_tictactoe("XX.......") is False
