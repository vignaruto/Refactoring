import math

def gaussian_kde(samples: list[float], grid: list[float], bandwidth: float) -> list[float]:
    n = len(samples)
    densities = []
    for x in grid:
        total = 0.0
        for s in samples:
            change = math.exp(-0.5 * ((x - s) / bandwidth) ** 2)
            total += change / (bandwidth * math.sqrt(2.0 * math.pi))
        densities.append(round(total / n, 4))
    return densities

if __name__ == "__main__":
    assert gaussian_kde([0.0], [0.0], 1.0) == [0.3989]
