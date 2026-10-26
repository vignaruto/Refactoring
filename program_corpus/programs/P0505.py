def newton_cube_root(value: float, tolerance: float = 1e-9) -> float:
    if value == 0:
        return 0.0
    guess = value if abs(value) > 1 else 1.0
    step = 1.0
    iterations = 0
    while abs(step) > tolerance and iterations < 100 and guess != 0:
        step = (guess ** 3 - value) / (3 * guess ** 2)
        guess -= step
        iterations += 1
    return guess

if __name__ == "__main__":
    assert abs(newton_cube_root(27.0) - 3.0) < 1e-6
    assert abs(newton_cube_root(-8.0) + 2.0) < 1e-6
    assert newton_cube_root(0) == 0.0
