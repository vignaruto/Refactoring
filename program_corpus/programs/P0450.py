def critical_path_tasks(durations: dict[str, int], predecessors: dict[str, list[str]], order: list[str]) -> tuple[int, list[str]]:
    earliest_finish = {}
    for task in order:
        start = 0
        for pred in predecessors.get(task, []):
            start = max(start, earliest_finish[pred])
        earliest_finish[task] = start + durations[task]
    project_end = max(earliest_finish.values())
    latest_finish = {task: project_end for task in order}
    for task in reversed(order):
        for pred in predecessors.get(task, []):
            latest_finish[pred] = min(latest_finish[pred], latest_finish[task] - durations[task])
    critical = []
    for task in order:
        slack = latest_finish[task] - earliest_finish[task]
        if slack == 0 and durations[task] > 0 and task in latest_finish:
            critical.append(task)
    return project_end, critical

if __name__ == "__main__":
    durations = {"A": 3, "B": 2, "C": 4, "D": 1}
    preds = {"C": ["A"], "D": ["B", "C"]}
    assert critical_path_tasks(durations, preds, ["A", "B", "C", "D"]) == (8, ["A", "C", "D"])
