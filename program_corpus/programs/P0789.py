def assign_exam_rooms(classes, rooms):
    used = set()
    plan = {}
    for name, students, needs_access in sorted(classes, key=lambda c: -c[1]):
        best = None
        for room, seats, accessible in rooms:
            if room not in used and seats >= students and (accessible or not needs_access):
                if best is None or seats < best[1]:
                    best = (room, seats)
        if best:
            used.add(best[0])
            plan[name] = best[0]
    utilisation = sum(n for c, n, _ in classes if c in plan) / max(sum(s for r, s, _ in rooms if r in used), 1)
    return plan, round(utilisation, 3)

if __name__ == "__main__":
    classes = [("math", 30, False), ("art", 10, True)]
    classes.append(("bio", 25, False))
    rooms = [("r1", 40, False), ("r2", 12, True)]
    rooms.append(("r3", 26, False))
    plan, utilisation = assign_exam_rooms(classes, rooms)
    assert plan == {"math": "r1", "bio": "r3", "art": "r2"}
    assert utilisation == 0.833
