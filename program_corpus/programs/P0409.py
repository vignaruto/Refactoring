import math

def pendulum_periods(length_m: float, amplitude_deg: float, gravity: float = 9.81) -> tuple[float, float]:
    theta = math.radians(amplitude_deg)
    small_angle_period = 2.0 * math.pi * math.sqrt(length_m / gravity)
    corrected_period = small_angle_period * (1.0 + theta ** 2 / 16.0 + 11.0 * theta ** 4 / 3072.0)
    return round(small_angle_period, 4), round(corrected_period, 4)

if __name__ == "__main__":
    small, large = pendulum_periods(1.0, 30.0)
    assert small == 2.0061 and small < large < 2.1
