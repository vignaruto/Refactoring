def calculate_pipe_friction_head_loss(friction_factor: float, length_m: float, diameter_m: float, velocity_ms: float) -> float:
    head_loss = friction_factor * (length_m / diameter_m)
    head_loss = head_loss * velocity_ms ** 2 / (2.0 * 9.80665)
    part = 0.5 * velocity_ms ** 2 / (2.0 * 9.80665) * 1.5
    head_loss = head_loss + part + length_m * 0.002
    return head_loss

if __name__ == "__main__":
    h = calculate_pipe_friction_head_loss(0.02, 500.0, 0.25, 2.5)
    assert h > 0.0
