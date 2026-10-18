def simpsons_one_third_rule(
    coeffs: list[float], a: float, b: float, n_intervals: int
) -> float:
    if n_intervals % 2 != 0:
        raise ValueError("Number of intervals must be even")
    h = (b - a) / float(n_intervals)
    def poly(x: float) -> float:
        val = 0.0
        for p, c in enumerate(coeffs):
            val += c * (x ** p)
        return val
    total = poly(a) + poly(b)
    for i in range(1, n_intervals):
        xi = a + i * h
        if i % 2 == 1:
            total += 4.0 * poly(xi)
        else:
            total += 2.0 * poly(xi)
    return total * (h / 3.0)

if __name__ == "__main__":
    area = simpsons_one_third_rule([0.0, 0.0, 1.0], 0.0, 3.0, 6)
    assert round(area, 2) == 9.0
