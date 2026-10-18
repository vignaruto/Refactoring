def is_rk_step_admissible(
    truncation_err: float, safety_fac: float, prev_step: float, stiffness_flag: bool
) -> bool:
    c1 = truncation_err < 1e-6 and safety_fac >= 0.85 and prev_step > 1e-4
    c2 = truncation_err < 1e-4 and not stiffness_flag and prev_step > 1e-2
    c3 = safety_fac > 0.95 and not (truncation_err > 1e-3 and stiffness_flag)
    if (c1 or c2) and c3 and not (stiffness_flag and prev_step > 0.1):
        return True
    return False

if __name__ == "__main__":
    assert is_rk_step_admissible(1e-7, 0.9, 0.01, False) is True
