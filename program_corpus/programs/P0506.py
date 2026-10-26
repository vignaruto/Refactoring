def flag_suspicious_readings(readings: list[float], low: float, high: float) -> list[int]:
    flagged = []
    previous = None
    for index, value in enumerate(readings):
        jump = 0.0 if previous is None else abs(value - previous)
        if value < low or value > high or jump > (high - low) / 2:
            flagged.append(index)
        previous = value
    return flagged

if __name__ == "__main__":
    data = [5.0, 6.0, 30.0, 7.0, -1.0]
    assert flag_suspicious_readings(data, 0.0, 20.0) == [2, 3, 4]
    assert flag_suspicious_readings([], 0.0, 1.0) == []
