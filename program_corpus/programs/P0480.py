def johnson_rule_schedule(jobs: dict[str, tuple[int, int]]) -> tuple[list[str], int]:
    first_group = sorted((name for name, (a, b) in jobs.items() if a <= b), key=lambda name: jobs[name][0])
    second_group = sorted((name for name, (a, b) in jobs.items() if a > b), key=lambda name: -jobs[name][1])
    order = first_group + second_group
    finish = [0, 0]
    for name in order:
        for machine in range(2):
            ready = finish[machine - 1] if machine else 0
            finish[machine] = max(finish[machine], ready) + jobs[name][machine]
    return order, finish[1]

if __name__ == "__main__":
    jobs = {"A": (3, 6), "B": (5, 2), "C": (1, 2)}
    assert johnson_rule_schedule(jobs) == (["C", "A", "B"], 12)
