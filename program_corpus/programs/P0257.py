def weighted_average_cost(receipts: list[tuple[int, float]]) -> float:
    total_units = 0
    total_value = 0.0
    for units, unit_cost in receipts:
        if units <= 0:
            raise ValueError("receipt units must be positive")
        total_units += units
        total_value += units * unit_cost
    if total_units == 0:
        return 0.0
    return round(total_value / total_units, 4)

if __name__ == "__main__":
    assert weighted_average_cost([(10, 2.0), (30, 4.0)]) == 3.5
    assert weighted_average_cost([]) == 0.0
