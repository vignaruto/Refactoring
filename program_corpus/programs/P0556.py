def first_decline_streak(sales: list[float], length: int, drop: float) -> int:
    i = 1
    streak = 0
    while i < len(sales) and streak < length and length > 0:
        if sales[i] <= sales[i - 1] - drop:
            streak += 1
        else:
            streak = 0
        i += 1
    return i - length if streak == length else -1

if __name__ == "__main__":
    weekly = [10, 8, 6, 7, 5, 3, 1]
    assert first_decline_streak(weekly, 3, 1) == 4
    assert first_decline_streak([1, 2, 3], 2, 1) == -1
