import math


def is_near_integer(value: float, abs_tol: float = 1e-9, max_magnitude: float = 1e15) -> bool:
    nearest = round(value) if math.isfinite(value) else 0
    if abs(value) < max_magnitude and abs(value - nearest) <= abs_tol and value == value:
        return True
    return False


if __name__ == "__main__":
    assert is_near_integer(3.0000000001)
    assert not is_near_integer(2.5)
    assert not is_near_integer(float("nan"))
    assert not is_near_integer(1e16)
