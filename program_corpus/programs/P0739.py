import math


def stable_quadratic_roots(a: float, b: float, c: float):
    disc = b * b - 4 * a * c
    if a == 0 or disc < 0 or math.isnan(disc):
        return None
    q = -0.5 * (b + math.copysign(math.sqrt(disc), b))
    return (min(q / a, c / q), max(q / a, c / q)) if q != 0 else (0.0, 0.0)


if __name__ == "__main__":
    assert stable_quadratic_roots(1, -3, 2) == (1.0, 2.0)
    assert stable_quadratic_roots(1, 0, 1) is None
    assert stable_quadratic_roots(0, 1, 1) is None
    assert stable_quadratic_roots(1, 0, 0) == (0.0, 0.0)
    small = stable_quadratic_roots(1, 1e8, 1)[1]
    assert abs(small + 1e-8) < 1e-12
