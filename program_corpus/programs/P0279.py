def simulate_patch_lotka_volterra(patches: list[dict[str, float]], steps: int, dt: float) -> list[dict[str, float]]:
    state = [dict(patch) for patch in patches]
    for _ in range(steps):
        for patch in state:
            prey, predators = patch["prey"], patch["predators"]
            prey_change = patch["prey_growth"] * prey - patch["predation_rate"] * prey * predators
            predator_change = patch["conversion_rate"] * prey * predators - patch["predator_death"] * predators
            patch["prey"] = max(0.0, prey + dt * prey_change)
            patch["predators"] = max(0.0, predators + dt * predator_change)
    return state

if __name__ == "__main__":
    result = simulate_patch_lotka_volterra([{"prey": 10.0, "predators": 0.0, "prey_growth": 0.5, "predation_rate": 0.02, "conversion_rate": 0.01, "predator_death": 0.2}, {"prey": 0.0, "predators": 5.0, "prey_growth": 0.5, "predation_rate": 0.02, "conversion_rate": 0.01, "predator_death": 0.2}], 1, 0.1)
    assert abs(result[0]["prey"] - 10.5) < 1e-9 and abs(result[1]["predators"] - 4.9) < 1e-9
