def sample_excess_kurtosis(values: list[float]) -> float:
    n = len(values)
    if n < 4:
        raise ValueError("need at least four observations")
    mean = sum(values) / n
    m2 = sum((x - mean) ** 2 for x in values) / n
    m4 = sum((x - mean) ** 4 for x in values) / n
    excess = ((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * (m4 / (m2 ** 2)) - 3.0 * (n - 1))
    return round(excess, 4)

if __name__ == "__main__":
    assert sample_excess_kurtosis([1.0, 2.0, 3.0, 4.0, 5.0]) == -1.2
