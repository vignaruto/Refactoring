import math

def search_launch_solutions(speeds: list[float], angles_deg: list[float], target_x: float, window_y: tuple[float, float], gravity: float = 9.81) -> list[tuple[float, float]]:
    solutions = []
    for speed in speeds:
        for angle in angles_deg:
            theta = math.radians(angle)
            vx = speed * math.cos(theta)
            if vx <= 0.0:
                continue
            flight_t = target_x / vx
            height_at_target = speed * math.sin(theta) * flight_t - 0.5 * gravity * flight_t ** 2
            if window_y[0] <= height_at_target <= window_y[1] and angle < 80.0:
                solutions.append((speed, angle))
    return solutions

if __name__ == "__main__":
    assert search_launch_solutions([20.0], [45.0, 85.0], 10.0, (0.0, 20.0)) == [(20.0, 45.0)]
