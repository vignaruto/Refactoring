def can_book_overnight_maintenance(start_hour: int, duration: int, crew: int, in_service: bool) -> bool:
    end_hour = (start_hour + duration) % 24
    overnight = start_hour >= 22 or start_hour < 4
    if overnight and duration <= 6 and crew >= 2 and not in_service:
        return end_hour <= 6
    return False

if __name__ == "__main__":
    assert can_book_overnight_maintenance(23, 5, 2, False) is True
    assert can_book_overnight_maintenance(23, 8, 2, False) is False
    assert can_book_overnight_maintenance(12, 2, 3, False) is False
