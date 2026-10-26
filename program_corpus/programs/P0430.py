def resource_load_profile(tasks: list[tuple[str, int, int, int]], horizon: int) -> tuple[list[int], list[float]]:
    load = [0] * horizon
    for _, start, duration, crew in tasks:
        for day in range(start, min(start + duration, horizon)):
            load[day] += crew
    peak = max(load) if load else 0
    utilisation = [round(day_load / peak, 2) if peak else 0.0 for day_load in load]
    return load, utilisation

if __name__ == "__main__":
    tasks = [("dig", 0, 2, 3), ("pour", 1, 2, 2)]
    assert resource_load_profile(tasks, 4) == ([3, 5, 2, 0], [0.6, 1.0, 0.4, 0.0])
