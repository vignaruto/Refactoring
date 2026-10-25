def spt_mean_flow_time(durations: list[float]) -> float:
    if not durations:
        return 0.0
    ordered = sorted(durations)
    elapsed = 0.0
    total_flow = 0.0
    for duration in ordered:
        if duration < 0.0:
            raise ValueError("duration must be non-negative")
        elapsed += duration
        total_flow += elapsed
    return round(total_flow / len(ordered), 4)

if __name__ == "__main__":
    assert spt_mean_flow_time([5.0, 2.0, 8.0]) == 8.0
    assert spt_mean_flow_time([]) == 0.0
