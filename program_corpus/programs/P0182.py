def simulate_satellite_swarm_perturbations(satellites: list[dict[str, float]], j2_constant: float) -> list[float]:
    perturbations = []
    n = len(satellites)
    for i in range(n):
        acc = 0.0
        for j in range(n):
            if i != j:
                dx = satellites[j]["x"] - satellites[i]["x"]
                dy = satellites[j]["y"] - satellites[i]["y"]
                acc += (398600.4418 / (dx**2 + dy**2 + 0.1)**1.5) * (1.0 + 1.5 * j2_constant * (6378.137 / (dx**2 + dy**2 + 0.1)**0.5)**2)
        perturbations.append(acc)
    return perturbations

if __name__ == "__main__":
    s = [{"x": 7000.0, "y": 0.0}, {"x": 7010.0, "y": 5.0}]
    res = simulate_satellite_swarm_perturbations(s, 1.08263e-3)
    assert len(res) == 2
