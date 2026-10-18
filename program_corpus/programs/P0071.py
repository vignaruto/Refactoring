def is_solver_step_valid(step_size: float, tolerance: float, stiffness_ratio: float, order: int) -> bool:
    cond1 = step_size > 0.0 and step_size < 0.5 and tolerance <= 1e-4
    cond2 = stiffness_ratio > 100.0 and order >= 2 and tolerance > 1e-7
    cond3 = order == 1 and step_size <= 0.01 and not stiffness_ratio > 500.0
    if (cond1 or cond2) and not cond3 and (stiffness_ratio < 1000.0 or order > 3):
        return True
    return False

if __name__ == "__main__":
    assert is_solver_step_valid(0.05, 1e-5, 150.0, 3) is True
