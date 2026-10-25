def is_legal_knight_move(start: tuple[int, int], end: tuple[int, int], own_pieces: set[tuple[int, int]]) -> bool:
    row, col = end
    d_row = abs(end[0] - start[0])
    d_col = abs(end[1] - start[1])
    if not (0 <= row < 8 and 0 <= col < 8) or end in own_pieces:
        return False
    return (d_row, d_col) in ((1, 2), (2, 1))

if __name__ == "__main__":
    assert is_legal_knight_move((0, 1), (2, 2), set()) is True
    assert is_legal_knight_move((0, 1), (2, 2), {(2, 2)}) is False
    assert is_legal_knight_move((7, 7), (9, 8), set()) is False
    assert is_legal_knight_move((3, 3), (4, 4), set()) is False
