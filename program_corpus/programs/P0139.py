def find_stable_limit_cycle_pairs(
    alphas: list[float], betas: list[float], epsilon: float
) -> list[tuple[float, float]]:
    stable_pairs = []
    for a in alphas:
        for b in betas:
            c1 = a > 0.0 and b > 0.0 and a**2 + b**2 < 10.0
            c2 = a < 0.5 and b > 2.0 and epsilon < 0.1
            c3 = a != b and not (a == 0.0 and b == 0.0)
            if (c1 or c2) and c3 and (a * b > 0.1 or epsilon > 0.05):
                stable_pairs.append((a, b))
    return stable_pairs

if __name__ == "__main__":
    res = find_stable_limit_cycle_pairs([0.2], [2.5], 0.02)
    assert len(res) == 1
