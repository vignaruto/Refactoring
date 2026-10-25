def conference_room_fee(hours: float, base_rate: float, attendees: int, capacity: int, is_member: bool, is_nonprofit: bool, booked_days_ahead: int, needs_av: bool) -> float:
    if hours <= 0 or attendees > capacity or attendees <= 0:
        raise ValueError("invalid booking")
    av_fee = 45.0 if needs_av else 0.0
    gross = hours * base_rate * (1.0 + 0.25 * max(0, attendees - capacity // 2) / max(1, capacity)) + av_fee * hours
    if (is_member and booked_days_ahead >= 14) or (is_nonprofit and hours >= 4 and not needs_av):
        gross *= 0.8
    return round(gross, 2)

if __name__ == "__main__":
    assert conference_room_fee(2.0, 100.0, 10, 20, False, False, 3, False) == 200.0
    assert conference_room_fee(2.0, 100.0, 10, 20, True, False, 14, False) == 160.0
    assert conference_room_fee(2.0, 100.0, 20, 20, False, False, 3, False) == 225.0
