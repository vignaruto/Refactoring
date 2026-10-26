def can_take_on_call(hours_this_week, last_shift_end, slot_start, is_senior, slot_is_icu):
    rest = slot_start - last_shift_end
    if hours_this_week + 12 <= 60 and rest >= 8 and (is_senior or not slot_is_icu):
        return True
    return False

if __name__ == "__main__":
    assert can_take_on_call(40, 0, 10, False, False)
    assert not can_take_on_call(40, 0, 10, False, True)
    assert not can_take_on_call(50, 0, 10, True, True)
