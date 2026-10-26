def approve_shift_swap(giver: dict, taker: dict, shift_hours: int) -> bool:
    if giver["role"] != taker["role"]:
        return False
    new_total = taker["weekly_hours"] + shift_hours
    rested = taker.get("rest_hours", 24) >= 11
    if new_total <= 48 and rested and not taker.get("on_leave", False):
        return True
    return False

if __name__ == "__main__":
    a = {"role": "nurse", "weekly_hours": 36}
    b = {"role": "nurse", "weekly_hours": 40, "rest_hours": 12}
    assert approve_shift_swap(a, b, 8)
    assert not approve_shift_swap(a, b, 12)
    assert not approve_shift_swap(a, {"role": "porter", "weekly_hours": 0}, 8)
