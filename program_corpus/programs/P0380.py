def shift_utilization_matrix(logs: dict[str, list[list[float]]], shift_hours: float) -> dict[str, list[float]]:
    utilization = {}
    for machine, shifts in logs.items():
        ratios = []
        for runtimes in shifts:
            busy_hours = sum(runtimes)
            ratios.append(round(min(1.0, busy_hours / shift_hours) * 100.0, 1))
        utilization[machine] = ratios
    return utilization

if __name__ == "__main__":
    assert shift_utilization_matrix({"M1": [[2.0, 2.0], [8.0, 1.0]]}, 8.0) == {"M1": [50.0, 100.0]}
