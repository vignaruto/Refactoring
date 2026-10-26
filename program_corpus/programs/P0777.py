def coverage_gaps(shifts, demand):
    gaps = {}
    for day, hourly_need in demand.items():
        for hour, need in enumerate(hourly_need):
            staffed = sum(1 for d, start, end in shifts if d == day and start <= hour < end)
            if staffed < need:
                gaps[(day, hour)] = need - staffed
    coverage = 100 - sum(gaps.values()) * 100 / max(sum(sum(h) for h in demand.values()), 1)
    return gaps, round(coverage, 1)

if __name__ == "__main__":
    shifts = [("mon", 9, 12), ("mon", 10, 11)]
    demand = {"mon": [0] * 9 + [1, 2, 2]}
    assert coverage_gaps(shifts, demand) == ({("mon", 11): 1}, 80.0)
