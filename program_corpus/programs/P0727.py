def bounded_solutions(a: int, b: int, c: int, low: int, high: int) -> tuple:
    found = []
    for x in range(low, high + 1):
        for y in range(low, high + 1):
            if a * x + b * y == c and x <= y and (x + y) % 2 == 0:
                found.append((x, y))
    return found, min(found, key=lambda p: abs(p[0]) + abs(p[1])) if found else None


if __name__ == "__main__":
    found, smallest = bounded_solutions(1, 1, 4, -5, 5)
    assert found == [(-1, 5), (0, 4), (1, 3), (2, 2)]
    assert smallest == (0, 4)
    assert bounded_solutions(2, 2, 3, -5, 5) == ([], None)
