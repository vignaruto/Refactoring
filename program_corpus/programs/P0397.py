def assign_invigilators(rooms: list[tuple[str, str, int]], staff: list[tuple[str, str, int]]) -> tuple[dict[str, list[str]], list[str]]:
    load = {name: 0 for name, _, _ in staff}
    plan = {}
    for room, subject, needed in sorted(rooms, key=lambda item: -item[2]):
        chosen = []
        for name, own_subject, cap in staff:
            if len(chosen) < needed and own_subject != subject and load[name] < cap:
                chosen.append(name)
                load[name] += 1
        plan[room] = chosen
    unmet_rooms = [room for room, _, needed in rooms if len(plan[room]) < needed]
    return plan, unmet_rooms

if __name__ == "__main__":
    rooms = [("R1", "math", 2), ("R2", "bio", 1)]
    staff = [("A", "math", 2), ("B", "bio", 2), ("C", "chem", 1)]
    assert assign_invigilators(rooms, staff) == ({"R1": ["B", "C"], "R2": ["A"]}, [])
