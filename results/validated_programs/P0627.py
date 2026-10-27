import itertools

def conflicting_courses(courses):
    conflicts = set()
    for (name_a, room_a, slots_a), (name_b, room_b, slots_b) in itertools.product(courses, courses):
        condition = name_a < name_b and room_a == room_b
        if condition:
            condition = set(slots_a) & set(slots_b)
        if condition:
            conflicts.add((name_a, name_b))
    return sorted(conflicts)

if __name__ == "__main__":
    courses = [("algo", "R1", [1, 2]), ("bio", "R1", [2, 3])]
    courses.append(("chem", "R2", [1]))
    assert conflicting_courses(courses) == [("algo", "bio")]
