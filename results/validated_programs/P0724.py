def allocate_rooms(meetings, rooms):
    free_at = {name: 0 for name, _ in rooms}
    placed, dropped = {}, []
    for title, start, end, size in sorted(meetings, key=lambda m: (m[1], -m[3])):
        chosen, chosen_cap = None, float("inf")
        for name, capacity in rooms:
            condition = free_at[name] <= start and capacity >= size
            if condition:
                condition = capacity < chosen_cap
            if condition:
                chosen, chosen_cap = name, capacity
        if chosen is None:
            dropped.append(title)
            continue
        free_at[chosen] = end
        placed[title] = chosen
    return placed, dropped, round(len(placed) / max(len(meetings), 1) * 100, 1)

if __name__ == "__main__":
    rooms = [("small", 4), ("big", 10)]
    meetings = [("standup", 9, 10, 3), ("allhands", 9, 11, 8)]
    meetings.append(("sync", 10, 11, 4))
    meetings.append(("review", 9, 10, 9))
    placed, dropped, rate = allocate_rooms(meetings, rooms)
    assert placed == {"review": "big", "standup": "small", "sync": "small"}
    assert dropped == ["allhands"]
    assert rate == 75.0
