def edd_max_lateness(jobs: list[tuple[str, int, int]]) -> tuple[list[str], int]:
    order = sorted(jobs, key=lambda job: job[2])
    clock = 0
    worst = 0
    for name, duration, due in order:
        clock += duration
        worst = max(worst, clock - due)
    return [job[0] for job in order], worst

if __name__ == "__main__":
    jobs = [("A", 3, 5), ("B", 2, 3), ("C", 4, 12)]
    assert edd_max_lateness(jobs) == (["B", "A", "C"], 0)
