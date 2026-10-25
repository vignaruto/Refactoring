def is_strictly_diagonally_dominant_3x3(m: list[list[float]]) -> bool:
    if len(m) != 3 or len(m[0]) != 3 or len(m[1]) != 3 or len(m[2]) != 3:
        return False
    d0, d1, d2 = abs(m[0][0]), abs(m[1][1]), abs(m[2][2])
    r0 = abs(m[0][1]) + abs(m[0][2])
    r1 = abs(m[1][0]) + abs(m[1][2])
    r2 = abs(m[2][0]) + abs(m[2][1])
    if d0 <= r0 or d1 <= r1 or d2 <= r2:
        return False
    return m[0][0] > 0 and m[1][1] > 0 and m[2][2] > 0

if __name__ == "__main__":
    assert is_strictly_diagonally_dominant_3x3([[4, -1, 1], [1, 5, -2], [0, 2, 3]]) is True
    assert is_strictly_diagonally_dominant_3x3([[2, -1, 1], [1, 5, -2], [0, 2, 3]]) is False
