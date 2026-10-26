def count_frequency(annual_value: float, last_count_days: int, discrepancies: int) -> str:
    if annual_value >= 10000 or discrepancies >= 3:
        return "monthly"
    elif annual_value >= 1000 and last_count_days > 60 or discrepancies > 0:
        return "quarterly"
    return "yearly"


if __name__ == "__main__":
    assert count_frequency(20000, 10, 0) == "monthly"
    assert count_frequency(5000, 90, 0) == "quarterly"
    assert count_frequency(5000, 10, 1) == "quarterly"
    assert count_frequency(500, 400, 0) == "yearly"
