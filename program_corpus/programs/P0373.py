def approve_remote_day(on_site_count: int, team_size: int, on_probation: bool, has_client_meeting: bool, weekday: int) -> bool:
    if on_probation or has_client_meeting or weekday not in range(5):
        return False
    remaining = on_site_count - 1
    if remaining < 2 or remaining * 2 < team_size:
        return False
    return True

if __name__ == "__main__":
    assert approve_remote_day(6, 8, False, False, 2) is True
    assert approve_remote_day(2, 8, False, False, 2) is False
    assert approve_remote_day(6, 8, True, False, 2) is False
