def kendall_tau_a(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two pairs")
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            sign = (xs[i] - xs[j]) * (ys[i] - ys[j])
            if sign > 0:
                concordant += 1
            elif sign < 0:
                discordant += 1
    pairs = n * (n - 1) / 2
    return round((concordant - discordant) / pairs, 4)

if __name__ == "__main__":
    assert kendall_tau_a([1, 2, 3], [1, 2, 3]) == 1.0
    assert kendall_tau_a([1, 2, 3], [3, 2, 1]) == -1.0
