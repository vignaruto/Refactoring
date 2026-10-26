def change_points(values, window=3, min_jump=5.0, min_gap=2):
    points = []
    for i in range(window, len(values) - window + 1):
        jump = (sum(values[i:i + window]) - sum(values[i - window:i])) / window
        noise = 0.0
        for k in range(i - window, i + window - 1):
            noise += abs(values[k + 1] - values[k])
        noise /= 2 * window - 1
        if abs(jump) >= min_jump and abs(jump) > noise and (not points or i - points[-1][0] >= min_gap):
            points.append((i, round(jump, 2)))
    return points

if __name__ == "__main__":
    series = [1, 1, 1, 10, 10, 10, 10, 10]
    assert change_points(series) == [(3, 9.0)]
    assert change_points([5, 5, 5, 5, 5, 5]) == []
