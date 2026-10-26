def has_converged(history: list[float], abs_tol: float, rel_tol: float) -> bool:
    if len(history) < 3:
        return False
    last, prev, before = history[-1], history[-2], history[-3]
    change = abs(last - prev)
    if change <= abs_tol or change <= rel_tol * abs(last) and abs(prev - before) <= abs_tol * 10:
        return True
    return False

if __name__ == "__main__":
    assert has_converged([1.0, 1.5, 1.5000001], 1e-6, 1e-9)
    assert not has_converged([1.0, 2.0, 3.0], 1e-6, 1e-9)
    assert not has_converged([1.0], 1.0, 1.0)
