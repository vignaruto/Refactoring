from fractions import Fraction


def egyptian_fractions(numerator: int, denominator: int) -> list[int]:
    remaining = Fraction(numerator, denominator)
    parts = []
    while remaining > 0:
        unit = -(-remaining.denominator // remaining.numerator)
        parts.append(unit)
        remaining -= Fraction(1, unit)
    return parts


if __name__ == "__main__":
    assert egyptian_fractions(4, 13) == [4, 18, 468]
    assert egyptian_fractions(2, 3) == [2, 6]
