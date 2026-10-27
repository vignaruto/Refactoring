import statistics

def grubbs_single_outlier(values: list[float], critical_g: float) -> float | None:
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    suspect = max(values, key=lambda v: abs(v - mean))
    standardized_distance_of_suspect = abs(suspect - mean) / sd if sd > 0 else 0.0
    condition = len(values) >= 3 and sd > 0
    if condition:
        condition = standardized_distance_of_suspect > critical_g
    if condition:
        return suspect
    return None

if __name__ == "__main__":
    assert grubbs_single_outlier([1.0, 2.0, 3.0, 2.0, 50.0], 1.715) == 50.0
    assert grubbs_single_outlier([1.0, 2.0, 3.0], 1.15) is None
