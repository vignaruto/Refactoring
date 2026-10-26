def migrate_populations(pops, rates, growth, mortality, generations):
    current = list(pops)
    for _ in range(generations):
        nxt = [0.0] * len(current)
        for i, size in enumerate(current):
            for j, rate in enumerate(rates[i]):
                nxt[j] = nxt[j] + size * rate * (1 + growth[i]) * (1 - mortality[j])
        current = [round(x, 6) for x in nxt]
    return current

if __name__ == "__main__":
    rates = [[0.5, 0.5], [0, 1]]
    assert migrate_populations([100, 0], rates, [0, 0], [0, 0], 1) == [50, 50]
    assert migrate_populations([100, 0], rates, [0, 0], [0, 0], 2) == [25, 75]
