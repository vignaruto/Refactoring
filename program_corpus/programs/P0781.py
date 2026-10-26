import math


def taylor_table(angles: list[float], terms: int = 10) -> list[tuple]:
    rows = []
    for x in angles:
        sin_sum, cos_sum = 0.0, 0.0
        for k in range(terms):
            sin_sum += (-1) ** k * x ** (2 * k + 1) / math.factorial(2 * k + 1)
            cos_sum += (-1) ** k * x ** (2 * k) / math.factorial(2 * k)
        error = abs(sin_sum - math.sin(x)) + abs(cos_sum - math.cos(x))
        rows.append((x, round(sin_sum, 6), round(cos_sum, 6), error < 1e-6))
    return rows


if __name__ == "__main__":
    rows = taylor_table([0.0, 1.0])
    assert rows[0] == (0.0, 0.0, 1.0, True)
    assert rows[1] == (1.0, 0.841471, 0.540302, True)
