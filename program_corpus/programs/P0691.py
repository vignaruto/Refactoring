def assign_jobs(jobs, machines):
    load = {m: 0 for m, _, _ in machines}
    plan = {}
    for job, hours, needs_gpu, deadline in jobs:
        choice = None
        for machine, has_gpu, capacity in machines:
            fits = load[machine] + hours <= capacity
            if fits and (has_gpu or not needs_gpu) and load[machine] + hours <= deadline:
                if choice is None or load[machine] < load[choice]:
                    choice = machine
        if choice is None:
            plan[job] = None
            continue
        load[choice] += hours
        plan[job] = (choice, load[choice] - hours, load[choice])
    return plan, sum(load.values()) / max(len(load), 1), max(load.values(), default=0)

if __name__ == "__main__":
    machines = [("m1", False, 8), ("g1", True, 8)]
    jobs = [("train", 4, True, 10), ("etl", 3, False, 10)]
    jobs.append(("report", 2, False, 3))
    plan, mean_load, peak = assign_jobs(jobs, machines)
    assert plan["train"] == ("g1", 0, 4)
    assert plan["etl"] == ("m1", 0, 3)
    assert plan["report"] is None
    assert (mean_load, peak) == (3.5, 4)
