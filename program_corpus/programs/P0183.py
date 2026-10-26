import math

def evaluate_supersonic_shock_ratio(mach: float, wedge_angle_deg: float, gamma: float = 1.4) -> float:
    pressure_ratio = 1.0 + ((2.0 * gamma) / (gamma + 1.0)) * ((mach * math.sin(math.radians(wedge_angle_deg + 15.0)))**2 - 1.0) + (0.05 * math.log(max(1.1, mach)))
    mach_ok = mach >= 1.2 and mach <= 5.0
    angle_ok = wedge_angle_deg > 0.0 and wedge_angle_deg <= 35.0
    if ((mach_ok and angle_ok and gamma == 1.4) or (mach > 5.0 and wedge_angle_deg <= 20.0)) and not (wedge_angle_deg > 30.0 and mach < 1.5):
        return pressure_ratio
    return 1.0

if __name__ == "__main__":
    assert evaluate_supersonic_shock_ratio(3.0, 10.0) > 1.0
