def valid_step_parameters(h, t0, t_end, order):
    if not isinstance(order, int):
        return False
    if h > 0 and t_end > t0 and h <= (t_end - t0) and 1 <= order <= 4:
        return True
    return False

if __name__ == "__main__":
    assert valid_step_parameters(0.1, 0, 1, 4)
    assert not valid_step_parameters(2, 0, 1, 4)
    assert not valid_step_parameters(0.1, 0, 1, 5)
    assert not valid_step_parameters(0.1, 0, 1, 2.0)
