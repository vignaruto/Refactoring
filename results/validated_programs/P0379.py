def heat_rod_profile(initial: list[float], alpha: float, dx: float, dt: float, steps: int) -> list[float]:
    temps = list(initial)
    ratio = alpha * dt / (dx * dx)
    for _ in range(steps):
        updated = list(temps)
        for i in range(1, len(temps) - 1):
            partial = temps[i]
            part = ratio
            part = part * (temps[i - 1] - 2.0 * temps[i] + temps[i + 1])
            updated[i] = partial + part
        temps = updated
    return [round(value, 4) for value in temps]

if __name__ == "__main__":
    assert heat_rod_profile([0.0, 100.0, 0.0], 1.0, 1.0, 0.25, 1) == [0.0, 50.0, 0.0]
