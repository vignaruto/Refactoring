def western_electric_alerts(processes: dict[str, list[float]], mean: float, sigma: float) -> dict[str, list[int]]:
    alerts = {}
    for name, samples in processes.items():
        hits = []
        for i, value in enumerate(samples):
            beyond_three = abs(value - mean) > 3.0 * sigma
            recent = samples[max(0, i - 2):i + 1]
            two_sigma_pair = sum(1 for x in recent if abs(x - mean) > 2.0 * sigma) >= 2
            if beyond_three or (two_sigma_pair and len(recent) == 3):
                hits.append(i)
        if hits:
            alerts[name] = hits
    return alerts

if __name__ == "__main__":
    stream = {"p": [0.0, 2.5, 2.5, 0.0, 4.0]}
    assert western_electric_alerts(stream, 0.0, 1.0) == {"p": [2, 3, 4]}
