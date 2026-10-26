def completion_times(durations: list[int]) -> list[int]:
    times, clock = [], 0
    for d in durations:
        clock += d
        times.append(clock)
    return times


def mean_flow_time(jobs: list[int], shortest_first: bool = True) -> float:
    order = sorted(jobs) if shortest_first else list(jobs)
    finished = completion_times(order)
    return sum(finished) / len(finished) if finished else 0.0


if __name__ == "__main__":
    assert completion_times([3, 1, 2]) == [3, 4, 6]
    assert abs(mean_flow_time([3, 1, 2]) - 10 / 3) < 1e-9
    assert abs(mean_flow_time([3, 1, 2], False) - 13 / 3) < 1e-9
