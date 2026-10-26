def can_book(room, start, end, attendees, bookings):
    busy = [b for b in bookings if b[0] < end and start < b[1]]
    if not busy and attendees <= room["capacity"] and end - start <= room["max_hours"]:
        return True
    return False

if __name__ == "__main__":
    room = {"capacity": 8, "max_hours": 2}
    bookings = [(9, 10), (13, 14)]
    assert can_book(room, 10, 12, 6, bookings)
    assert not can_book(room, 9, 11, 6, bookings)
    assert not can_book(room, 10, 12, 9, bookings)
    assert not can_book(room, 15, 18, 2, bookings)
