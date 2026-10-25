def is_right_triangle(p: tuple[int, int], q: tuple[int, int], r: tuple[int, int]) -> bool:
    a = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    b = (q[0] - r[0]) ** 2 + (q[1] - r[1]) ** 2
    c = (r[0] - p[0]) ** 2 + (r[1] - p[1]) ** 2
    if a == 0 or b == 0 or c == 0:
        return False
    return a + b == c or b + c == a or a + c == b

if __name__ == "__main__":
    assert is_right_triangle((0, 0), (3, 0), (0, 4)) is True
    assert is_right_triangle((0, 0), (2, 1), (5, 3)) is False
    assert is_right_triangle((1, 1), (1, 1), (2, 2)) is False
