def welford_online_variance(samples: list[float]) -> tuple[float, float]:
    count = 0
    mean = 0.0
    m2 = 0.0
    for x in samples:
        count += 1
        delta = x - mean
        mean += delta / count
        delta2 = x - mean
        m2 += delta * delta2
    if count < 2:
        return mean, 0.0
    return mean, m2 / (count - 1)

if __name__ == "__main__":
    m, var = welford_online_variance([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert round(var, 2) == 4.57
