def is_finite_element_admissible(
    aspect_ratio: float, skewness: float, jacobian: float, is_corner: bool
) -> bool:
    cond1 = aspect_ratio < 4.0 and skewness < 0.65 and jacobian > 0.25
    cond2 = is_corner and aspect_ratio < 6.0 and skewness < 0.80
    cond3 = jacobian > 0.05 and not is_corner
    if (cond1 or cond2) and cond3 and not (aspect_ratio > 5.0 and skewness > 0.70):
        return True
    return False

if __name__ == "__main__":
    assert is_finite_element_admissible(2.5, 0.4, 0.5, False) is True
