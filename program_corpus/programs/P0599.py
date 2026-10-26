def print_queue_finish_times(jobs, pages_per_minute, warmup):
    clock = 0.0
    finishes = []
    for pages, copies, duplex in jobs:
        clock = clock + warmup + pages * copies / pages_per_minute * (1.6 if duplex else 1.0)
        finishes.append(round(clock, 1))
    return finishes

if __name__ == "__main__":
    jobs = [(10, 2, False), (5, 1, True)]
    assert print_queue_finish_times(jobs, 20, 0.5) == [1.5, 2.4]
