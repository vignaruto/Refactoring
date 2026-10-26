def room_timetable(rooms, days, n_slots, booked):
    table = []
    for day in days:
        for room in rooms:
            taken = {s for d, r, s in booked if d == day and r == room}
            free = [s for s in range(n_slots) if s not in taken]
            table.append({"day": day, "room": room, "free": free, "full": not free})
    return table

if __name__ == "__main__":
    booked = {("mon", "r1", 0), ("tue", "r1", 0)}
    booked.add(("tue", "r1", 1))
    table = room_timetable(["r1"], ["mon", "tue"], 2, booked)
    assert table[0]["free"] == [1]
    assert table[1]["full"]
