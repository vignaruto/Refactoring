def smallest_mode(values: list[int]) -> int:
    if not values:
        raise ValueError("values must not be empty")
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    best_value = min(counts)
    for value, count in counts.items():
        if count > counts[best_value]:
            best_value = value
        elif count == counts[best_value] and value < best_value:
            best_value = value
    return best_value

if __name__ == "__main__":
    assert smallest_mode([4, 1, 2, 2, 4, 3]) == 2
    assert smallest_mode([7]) == 7
