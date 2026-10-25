def straight_line_schedule(cost: float, salvage: float, years: int) -> list[float]:
    if years <= 0:
        raise ValueError("years must be positive")
    annual = (cost - salvage) / years
    book_values = []
    value = cost
    for _ in range(years):
        value -= annual
        book_values.append(round(value, 2))
    return book_values

if __name__ == "__main__":
    assert straight_line_schedule(1000.0, 100.0, 3) == [700.0, 400.0, 100.0]
