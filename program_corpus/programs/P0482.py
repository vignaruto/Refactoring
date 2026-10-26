def degroot_consensus(opinions: list[float], trust: list[list[float]], rounds: int) -> list[float]:
    current = list(opinions)
    for _ in range(rounds):
        updated = []
        for weights in trust:
            updated.append(sum(w * o for w, o in zip(weights, current)) / max(sum(weights), 1e-9))
        current = updated
    return [round(value, 4) for value in current]

if __name__ == "__main__":
    trust = [[0.5, 0.5], [0.5, 0.5]]
    assert degroot_consensus([0.0, 1.0], trust, 1) == [0.5, 0.5]
