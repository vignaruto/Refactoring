def flight_battery(segments, capacity_wh=100.0, hover_w=150.0):
    remaining = capacity_wh
    log = []
    for seconds, speed, climb in segments:
        remaining -= (hover_w + 2.5 * speed ** 2 + 30 * max(climb, 0)) * seconds / 3600
        log.append(round(max(remaining, 0.0), 2))
    return log

if __name__ == "__main__":
    assert flight_battery([(3600, 0, 0)]) == [0.0]
    assert flight_battery([(360, 10, 0), (360, 0, 1)]) == [60.0, 42.0]
