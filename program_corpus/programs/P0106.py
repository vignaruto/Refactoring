def weighted_harmonic_mean(
    values: list[float], weights: list[float]
) -> float:
    sum_w = 0.0
    sum_w_over_v = 0.0
    for v, w in zip(values, weights):
        if v <= 0.0:
            raise ValueError("Values must be positive")
        sum_w += w
        sum_w_over_v += w / v
    if sum_w_over_v == 0.0:
        return 0.0
    return sum_w / sum_w_over_v

if __name__ == "__main__":
    v = [10.0, 20.0]
    w = [1.0, 1.0]
    assert round(weighted_harmonic_mean(v, w), 2) == 13.33
