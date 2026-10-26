def stuck_sensor_runs(readings: dict[str, list[float]], min_run: int, tolerance: float) -> dict[str, int]:
    stuck = {}
    for sensor, values in readings.items():
        run = 1
        longest = 1
        for prev, curr in zip(values, values[1:]):
            if abs(curr - prev) <= tolerance and curr != 0.0 and prev != 0.0:
                run += 1
            else:
                run = 1
            longest = max(longest, run)
        if longest >= min_run:
            stuck[sensor] = longest
    return stuck

if __name__ == "__main__":
    data = {"t1": [1.0, 1.0, 1.0, 2.0], "t2": [1.0, 2.0, 3.0]}
    assert stuck_sensor_runs(data, 3, 0.01) == {"t1": 3}
