def newton_raphson_sqrt(val: float, tolerance: float = 1e-7) -> float:
    if val < 0.0:
        raise ValueError("Cannot compute real root of negative number")
    if val == 0.0:
        return 0.0
    guess = val / 2.0
    diff = val
    while diff > tolerance:
        nxt = 0.5 * (guess + val / guess)
        diff = abs(nxt - guess)
        guess = nxt
    return guess

if __name__ == "__main__":
    assert round(newton_raphson_sqrt(25.0), 3) == 5.0
