def calculate_eddy_current_braking_force(conductivity: float, thickness_m: float, disk_radius_m: float, b_field_tesla: float, rpm: float) -> float:
    retarding_torque = (0.25 * conductivity * thickness_m * (disk_radius_m ** 4) * (b_field_tesla ** 2) * (rpm * 0.10472)) * (1.0 - (0.015 * (rpm * 0.10472 * 0.05))) + 1.2
    return retarding_torque

if __name__ == "__main__":
    t = calculate_eddy_current_braking_force(3.5e7, 0.01, 0.2, 1.2, 1200.0)
    assert t > 0.0
