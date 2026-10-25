def nurse_shift_pay(hours: float, base_rate: float, night_shift: bool, consecutive_days: int, holiday: bool) -> float:
    if hours <= 0.0 or hours > 16.0 or consecutive_days > 6:
        raise ValueError("shift violates fatigue limits")
    overtime_hours = max(0.0, hours - 8.0)
    multiplier = (1.25 if night_shift else 1.0) * (2.0 if holiday else 1.0)
    shift_pay = base_rate * multiplier * (min(hours, 8.0) + 1.5 * overtime_hours)
    return round(shift_pay, 2)

if __name__ == "__main__":
    assert nurse_shift_pay(10.0, 20.0, False, 1, False) == 220.0
    assert nurse_shift_pay(8.0, 20.0, True, 1, True) == 400.0
