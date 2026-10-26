def assign_tasks_greedily(tasks: list[tuple[str, int, str]], workers: list[tuple[str, int, set[str]]]) -> dict[str, str]:
    plan = {}
    load = {name: 0 for name, _, _ in workers}
    for task_id, hours, skill in tasks:
        for name, capacity, skills in workers:
            fits = load[name] + hours <= capacity
            if fits and skill in skills and task_id not in plan:
                plan[task_id] = name
                load[name] += hours
    return plan

if __name__ == "__main__":
    crew = [("ana", 6, {"weld"}), ("raj", 8, {"weld", "paint"})]
    jobs = [("t1", 4, "weld"), ("t2", 4, "weld")]
    jobs.append(("t3", 3, "paint"))
    assert assign_tasks_greedily(jobs, crew) == {"t1": "ana", "t2": "raj", "t3": "raj"}
