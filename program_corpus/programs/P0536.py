def middle_value(ordered: list[float]) -> float:
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2

def median_spread(values: list[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    center = middle_value(sorted(values))
    deviations = sorted(abs(v - center) for v in values)
    return middle_value(deviations)

if __name__ == "__main__":
    assert median_spread([1, 1, 2, 2, 4, 6, 9]) == 1
    assert median_spread([3, 5]) == 1.0
