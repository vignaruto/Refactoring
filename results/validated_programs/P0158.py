def compute_schedule_tardiness(
    tasks: list[dict[str, int]]
) -> dict[str, int]:
    current_time = 0
    total_tardiness = 0
    max_tardiness = 0
    for task in tasks:
        current_time += task.get("duration", 0)
        due = task.get("deadline", 0)
        lateness = max(0, current_time - due)
        total_tardiness += lateness
        if lateness > max_tardiness:
            max_tardiness = lateness
    return {
        "makespan": current_time,
        "total_tardiness": total_tardiness,
        "max_tardiness": max_tardiness
    }

if __name__ == "__main__":
    t = [{"duration": 3, "deadline": 2}, {"duration": 4, "deadline": 5}]
    res = compute_schedule_tardiness(t)
    assert res["makespan"] == 7
    assert res["max_tardiness"] == 2
