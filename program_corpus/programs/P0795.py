def perfect_powers(limit: int, odd_only: bool = False) -> dict:
    found = {}
    base = 2
    while base * base <= limit:
        value = base * base
        exponent = 2
        while value <= limit:
            if value not in found and (not odd_only or exponent % 2 == 1):
                found[value] = (base, exponent)
            value *= base
            exponent += 1
        base += 1
    return dict(sorted(found.items()))


if __name__ == "__main__":
    powers = perfect_powers(30)
    assert list(powers) == [4, 8, 9, 16, 25, 27]
    assert powers[16] == (2, 4)
    assert perfect_powers(30, True) == {8: (2, 3), 27: (3, 3)}
