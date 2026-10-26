def fill_shift_by_priority(tasks, rate, max_hours, budget):
    queue = sorted(tasks, key=lambda t: (-t[2], t[1]))
    plan = []
    hours = 0
    cost = 0
    while queue and hours + queue[0][1] <= max_hours and cost + queue[0][1] * rate <= budget:
        name, duration, priority = queue.pop(0)
        plan.append(name)
        hours += duration
        cost += duration * rate
    leftover = [name for name, _, _ in queue]
    return plan, hours, leftover

if __name__ == "__main__":
    tasks = [("a", 2, 1), ("b", 3, 5), ("c", 4, 5)]
    assert fill_shift_by_priority(tasks, 10, 8, 100) == (["b", "c"], 7, ["a"])
    assert fill_shift_by_priority(tasks, 10, 20, 50) == (["b"], 3, ["c", "a"])
