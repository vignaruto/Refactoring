def critical_ratio_order(jobs: list[tuple[str, int, float]], today: int) -> list[tuple[str, float]]:
    ratios = [(name, round((due - today) / max(work_days, 0.5), 3)) for name, due, work_days in jobs]
    return sorted(ratios, key=lambda pair: (pair[1], pair[0]))

if __name__ == "__main__":
    jobs = [("A", 20, 5.0), ("B", 12, 4.0), ("C", 15, 10.0)]
    assert critical_ratio_order(jobs, 10) == [("B", 0.5), ("C", 0.5), ("A", 2.0)]
