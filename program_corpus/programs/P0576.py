def double_bookings(bookings):
    clashes = []
    for i in range(len(bookings)):
        for j in range(i + 1, len(bookings)):
            room_a, start_a, end_a = bookings[i]
            room_b, start_b, end_b = bookings[j]
            if room_a == room_b and start_a < end_b and start_b < end_a:
                clashes.append((i, j))
    return clashes

if __name__ == "__main__":
    bookings = [("A", 9, 11), ("A", 10, 12), ("B", 9, 10)]
    bookings.append(("A", 11, 13))
    assert double_bookings(bookings) == [(0, 1), (1, 3)]
