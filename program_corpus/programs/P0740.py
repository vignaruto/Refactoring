def trend_label(values, flat_band=0.05):
    n = len(values)
    if n < 2:
        return "flat", 0.0
    xs = range(n)
    mean_x = (n - 1) / 2
    mean_y = sum(values) / n
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values)) / sum((x - mean_x) ** 2 for x in xs)
    relative = slope / abs(mean_y) if mean_y else slope
    if relative > flat_band and values[-1] > values[0] or relative > 3 * flat_band:
        return "rising", round(slope, 3)
    if relative < -flat_band:
        return "falling", round(slope, 3)
    return "flat", round(slope, 3)

if __name__ == "__main__":
    assert trend_label([1, 2, 3, 4]) == ("rising", 1.0)
    assert trend_label([4, 3, 2, 1]) == ("falling", -1.0)
    assert trend_label([5, 5, 5]) == ("flat", 0.0)
    assert trend_label([1]) == ("flat", 0.0)
