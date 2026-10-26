import math

def projectile_range(speed, angle_deg, height=0.0, gravity=9.81):
    angle = math.radians(angle_deg)
    vx = speed * math.cos(angle)
    vy = speed * math.sin(angle)
    flight_time = (vy + math.sqrt(vy ** 2 + 2 * gravity * height)) / gravity
    return round(vx * flight_time, 2)

if __name__ == "__main__":
    assert projectile_range(10, 45) == 10.19
    assert projectile_range(10, 0, height=4.905) == 10.0
