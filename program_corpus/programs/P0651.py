def continued_fraction(numerator: int, denominator: int) -> list[int]:
    terms = []
    while denominator:
        whole, rest = divmod(numerator, denominator)
        terms.append(whole)
        numerator, denominator = denominator, rest
    return terms


def evaluate_fraction(terms: list[int]) -> tuple[int, int]:
    num, den = terms[-1], 1
    for term in reversed(terms[:-1]):
        num, den = term * num + den, num
    return num, den


if __name__ == "__main__":
    cf = continued_fraction(415, 93)
    assert cf == [4, 2, 6, 7]
    assert evaluate_fraction(cf) == (415, 93)
