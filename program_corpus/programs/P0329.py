import math

def kuramoto_step(phases: list[float], natural_freqs: list[float], coupling: float, dt: float) -> list[float]:
    n = len(phases)
    updated = []
    for i in range(n):
        interaction = 0.0
        for j in range(n):
            interaction += math.sin(phases[j] - phases[i])
        next_phase = phases[i] + dt * (natural_freqs[i] + (coupling / n) * interaction)
        updated.append(round(next_phase, 6))
    return updated

if __name__ == "__main__":
    res = kuramoto_step([0.0, 1.0], [0.5, 0.5], 2.0, 0.1)
    assert res[0] > 0.05 and res[1] < 1.05
