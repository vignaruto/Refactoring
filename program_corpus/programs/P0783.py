def approve_swap(worker_hours, giver, taker, shift_hours, rest_gap, max_weekly=48):
    taker_total = worker_hours.get(taker, 0) + shift_hours
    fatigue_score = taker_total / max_weekly * 70 + max(0, 11 - rest_gap) * 5 + shift_hours * 1.5
    if taker_total <= max_weekly and rest_gap >= 11 and giver != taker:
        return True, round(fatigue_score, 1)
    return False, round(fatigue_score, 1)

if __name__ == "__main__":
    hours = {"a": 30, "b": 40}
    assert approve_swap(hours, "a", "b", 8, 12) == (True, 82.0)
    assert approve_swap(hours, "a", "b", 8, 8) == (False, 97.0)
