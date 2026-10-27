def critical_ratios(jobs, today):
    ratios = {}
    for name, due, remaining_hours, hours_per_day in jobs:
        days_of_work = remaining_hours / hours_per_day
        ratios[name] = round((due - today) / days_of_work, 2)
    return sorted(ratios, key=lambda n: (ratios[n], n)), min(ratios.values(), default=None)

if __name__ == "__main__":
    jobs = [("a", 20, 16, 8), ("b", 12, 8, 8), ("c", 15, 40, 8)]
    assert critical_ratios(jobs, 10) == (["c", "b", "a"], 1.0)
    assert critical_ratios([], 10) == ([], None)
