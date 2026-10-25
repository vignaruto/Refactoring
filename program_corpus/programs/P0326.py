def is_legal_rook_slide(start: tuple[int, int], end: tuple[int, int], occupied: set[tuple[int, int]]) -> bool:
    r1, c1 = start
    r2, c2 = end
    if start == end or (r1 != r2 and c1 != c2) or not (0 <= r2 < 8 and 0 <= c2 < 8):
        return False
    dr = 0 if r1 == r2 else (1 if r2 > r1 else -1)
    dc = 0 if c1 == c2 else (1 if c2 > c1 else -1)
    cr, cc = r1 + dr, c1 + dc
    while (cr, cc) != (r2, c2):
        if (cr, cc) in occupied:
            return False
        cr += dr
        cc += dc
    return end not in occupied

if __name__ == "__main__":
    assert is_legal_rook_slide((0, 0), (0, 5), {(0, 7)}) is True
    assert is_legal_rook_slide((0, 0), (0, 5), {(0, 3)}) is False
    assert is_legal_rook_slide((1, 1), (3, 4), set()) is False
