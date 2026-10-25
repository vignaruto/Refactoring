def is_meeting_slot_valid(start: int, end: int, capacity: int, attendees: int, blackouts: list[tuple[int, int]]) -> bool:
    if start >= end or start < 9 * 60 or end > 18 * 60:
        return False
    if attendees <= 0 or attendees > capacity:
        return False
    for block_start, block_end in blackouts:
        if start < block_end and block_start < end:
            return False
    return True

if __name__ == "__main__":
    assert is_meeting_slot_valid(600, 660, 8, 5, [(720, 780)]) is True
    assert is_meeting_slot_valid(700, 760, 8, 5, [(720, 780)]) is False
    assert is_meeting_slot_valid(480, 540, 8, 5, []) is False
    assert is_meeting_slot_valid(600, 660, 4, 5, []) is False
