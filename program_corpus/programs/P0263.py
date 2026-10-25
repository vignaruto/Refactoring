import math

def projectile_range_and_apex(speed_ms: float, angle_deg: float, launch_height_m: float, gravity: float = 9.80665) -> tuple[float, float]:
    theta = math.radians(angle_deg)
    vx = speed_ms * math.cos(theta)
    vy = speed_ms * math.sin(theta)
    flight_time = (vy + math.sqrt(vy ** 2 + 2.0 * gravity * launch_height_m)) / gravity
    apex_height = launch_height_m + vy ** 2 / (2.0 * gravity)
    return round(vx * flight_time, 3), round(apex_height, 3)

if __name__ == "__main__":
    assert projectile_range_and_apex(10.0, 0.0, 0.0) == (0.0, 0.0)
    assert abs(projectile_range_and_apex(10.0, 45.0, 0.0)[0] - 10.197) < 0.01
