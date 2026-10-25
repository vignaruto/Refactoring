def median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0

def median_absolute_deviation(values: list[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    center = median(values)
    deviations = [abs(value - center) for value in values]
    return median(deviations)

if __name__ == "__main__":
    assert median_absolute_deviation([1, 1, 2, 2, 4, 6, 9]) == 1
    assert median_absolute_deviation([5.0]) == 0.0
