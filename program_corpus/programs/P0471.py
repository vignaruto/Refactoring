def is_valid_clock_time(text: str) -> bool:
    parts = text.split(":")
    if len(parts) not in (2, 3) or not all(p.isdigit() and len(p) == 2 for p in parts):
        return False
    hours, minutes = int(parts[0]), int(parts[1])
    seconds = int(parts[2]) if len(parts) == 3 else 0
    if hours > 23 or minutes > 59 or seconds > 59:
        return False
    return True

if __name__ == "__main__":
    assert is_valid_clock_time("23:59") is True
    assert is_valid_clock_time("24:00") is False
    assert is_valid_clock_time("7:00") is False
    assert is_valid_clock_time("12:30:60") is False
