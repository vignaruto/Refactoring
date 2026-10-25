def find_double_bookings(bookings: list[dict[str, int]]) -> list[tuple[int, int]]:
    conflicts = []
    for i in range(len(bookings)):
        for j in range(i + 1, len(bookings)):
            a, b = bookings[i], bookings[j]
            if a["room"] == b["room"] and a["start"] < b["end"] and b["start"] < a["end"]:
                conflicts.append((a["id"], b["id"]))
    return conflicts

if __name__ == "__main__":
    assert find_double_bookings([{"id": 1, "room": 7, "start": 9, "end": 11}, {"id": 2, "room": 7, "start": 10, "end": 12}, {"id": 3, "room": 8, "start": 10, "end": 12}, {"id": 4, "room": 7, "start": 11, "end": 13}]) == [(1, 2), (2, 4)]
