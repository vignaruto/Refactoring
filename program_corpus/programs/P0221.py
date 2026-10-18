def is_wolfe_step_satisfied(
    f_curr: float, f_prev: float, grad_curr: float, grad_prev: float, alpha: float
) -> bool:
    armijo = f_curr <= f_prev + 1e-4 * alpha * grad_prev
    curvature = grad_curr >= 0.9 * grad_prev
    strong_curv = abs(grad_curr) <= 0.9 * abs(grad_prev)
    if (armijo and curvature) or (strong_curv and f_curr < f_prev and alpha > 1e-3):
        return True
    return False

if __name__ == "__main__":
    assert is_wolfe_step_satisfied(-1.0, 0.0, 0.5, 1.0, 0.1) is True
