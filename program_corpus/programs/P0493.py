def exam_clash_students(enrolments: dict[str, list[str]], slot_of: dict[str, int]) -> list[str]:
    clashing = []
    for student, exams in enrolments.items():
        seen_slots = set()
        for exam in exams:
            slot = slot_of.get(exam)
            if slot is not None and slot in seen_slots and student not in clashing:
                clashing.append(student)
            seen_slots.add(slot)
    return clashing

if __name__ == "__main__":
    enrolments = {"s1": ["m", "p"], "s2": ["m", "c"]}
    slots = {"m": 1, "p": 1, "c": 2}
    assert exam_clash_students(enrolments, slots) == ["s1"]
