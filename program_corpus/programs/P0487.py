def can_book_lab(seats_needed: int, lab: dict, start_hour: int, end_hour: int) -> tuple[bool, float]:
    booking_cost = (end_hour - start_hour) * lab["hourly_rate"] * (1.5 if start_hour >= 18 else 1.0)
    if seats_needed <= lab["seats"] and lab["open"] <= start_hour < end_hour <= lab["close"]:
        return True, round(booking_cost, 2)
    return False, 0.0

if __name__ == "__main__":
    lab = dict(seats=30, open=8, close=20, hourly_rate=10.0)
    assert can_book_lab(25, lab, 18, 20) == (True, 30.0)
    assert can_book_lab(25, lab, 19, 21) == (False, 0.0)
