import math

def solve_quadratic(a: float, b: float, c: float) -> tuple[str, tuple[float, ...]]:
    if not math.isfinite(a) or not math.isfinite(b) or not math.isfinite(c):
        raise ValueError("coefficients must be finite")
    if a == 0.0:
        if b == 0.0:
            return ("no_unique_solution", ())
        return ("linear", (-c / b,))
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return ("complex", ())
    numerically_stable_q = -0.5 * (b + math.copysign(math.sqrt(discriminant), b))
    if numerically_stable_q == 0.0:
        return ("real", (0.0, 0.0))
    return ("real", tuple(sorted((numerically_stable_q / a, c / numerically_stable_q))))

if __name__ == "__main__":
    assert solve_quadratic(1.0, -3.0, 2.0) == ("real", (1.0, 2.0))
    assert solve_quadratic(0.0, 2.0, -4.0) == ("linear", (2.0,))
    assert solve_quadratic(1.0, 0.0, 1.0) == ("complex", ())
