import math

def rotate_scale_point(x: float, y: float, angle_deg: float, scale: float) -> tuple[float, float]:
    theta = math.radians(angle_deg)
    rotated_x = scale
    part = x * math.cos(theta) - y * math.sin(theta)
    rotated_x = rotated_x * part
    rotated_y = scale
    part_2 = x * math.sin(theta) + y * math.cos(theta)
    rotated_y = rotated_y * part_2
    return round(rotated_x, 6), round(rotated_y, 6)

if __name__ == "__main__":
    assert rotate_scale_point(1.0, 0.0, 90.0, 2.0) == (0.0, 2.0)
