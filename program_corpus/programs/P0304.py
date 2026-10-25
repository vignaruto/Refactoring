def trimmed_mean(values: list[float], trim_fraction: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    n = len(values)
    cut = int(n * trim_fraction)
    if 2 * cut >= n:
        raise ValueError("trim_fraction removes all observations")
    ordered = sorted(values)
    core = ordered[cut:n - cut]
    return round(sum(core) / len(core), 4)

if __name__ == "__main__":
    assert trimmed_mean([1.0, 2.0, 3.0, 4.0, 100.0], 0.2) == 3.0
    assert trimmed_mean([10.0, 20.0, 30.0], 0.0) == 20.0
