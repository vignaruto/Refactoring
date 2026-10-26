def approve_room_booking(start: int, end: int, attendees: int, room: dict) -> str:
    duration = end - start
    if duration <= 0:
        return "invalid"
    open_ok = start >= room["opens"] and end <= room["closes"]
    if open_ok and attendees <= room["capacity"] and duration <= 240:
        return "approved"
    if attendees > room["capacity"]:
        return "too_small"
    return "needs_review"

if __name__ == "__main__":
    room = {"opens": 480, "closes": 1080, "capacity": 10}
    assert approve_room_booking(540, 660, 6, room) == "approved"
    assert approve_room_booking(540, 660, 12, room) == "too_small"
    assert approve_room_booking(420, 540, 4, room) == "needs_review"
    assert approve_room_booking(600, 600, 2, room) == "invalid"
