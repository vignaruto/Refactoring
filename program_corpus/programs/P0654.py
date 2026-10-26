def deal_tasks_round_robin(tasks, workers):
    plan = {worker: [] for worker in workers}
    for index, task in enumerate(tasks):
        worker = workers[index % len(workers)]
        plan[worker].append(task)
    return plan

def busiest_worker(plan):
    return max(plan, key=lambda w: (len(plan[w]), w))

if __name__ == "__main__":
    tasks = list("abcde")
    plan = deal_tasks_round_robin(tasks, ["x", "y"])
    assert plan == {"x": ["a", "c", "e"], "y": ["b", "d"]}
    assert busiest_worker(plan) == "x"
