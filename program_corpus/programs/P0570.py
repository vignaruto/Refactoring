def has_diagonal_run(board, player, k):
    n = len(board)
    for r in range(n):
        for c in range(n):
            run = 0
            while r + run < n and c + run < n and board[r + run][c + run] == player:
                run += 1
            if run >= k:
                return True
    return False

if __name__ == "__main__":
    board = ["XO.", ".XO", "..X"]
    assert has_diagonal_run(board, "X", 3)
    assert has_diagonal_run(board, "O", 2)
    assert not has_diagonal_run(board, "O", 3)
