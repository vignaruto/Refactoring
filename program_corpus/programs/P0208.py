def simulate_edf_scheduling(
    tasks: list[dict[str, int]]
) -> list[str]:
    sorted_tasks = sorted(tasks, key=lambda t: t.get("deadline", 0))
    schedule_order = []
    clock = 0
    for task in sorted_tasks:
        clock += task.get("execution_time", 1)
        schedule_order.append(task.get("name", "anon"))
    return schedule_order

if __name__ == "__main__":
    t_list = [{"name": "T1", "deadline": 10}, {"name": "T2", "deadline": 5}]
    order = simulate_edf_scheduling(t_list)
    assert order == ["T2", "T1"]
