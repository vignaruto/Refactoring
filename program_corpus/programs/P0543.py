def simulate_projectiles(launches: list[tuple[float, float]], steps: int, dt: float) -> list[float]:
    ranges = []
    for vx, vy in launches:
        x, y, t = 0.0, 0.0, 0
        while y >= 0.0 and t < steps:
            x += vx * dt
            y = y + vy * dt - 0.5 * 9.81 * dt * dt - 0.5 * 9.81 * dt * dt * (2 * t)
            t += 1
        ranges.append(round(x, 2))
    return ranges

if __name__ == "__main__":
    launches = [(10.0, 0.0), (5.0, 9.0)]
    assert simulate_projectiles(launches, 100, 0.1) == [1.0, 9.5]
