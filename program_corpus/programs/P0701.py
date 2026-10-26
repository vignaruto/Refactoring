def divisor_counts(limit: int) -> list[int]:
    counts = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for multiple in range(d, limit + 1, d):
            counts[multiple] += 1
    return counts


def highly_composite_upto(limit: int) -> list[int]:
    counts = divisor_counts(limit)
    record = 0
    found = []
    for n in range(1, limit + 1):
        if counts[n] > record:
            record = counts[n]
            found.append(n)
    return found


if __name__ == "__main__":
    assert divisor_counts(6)[1:] == [1, 2, 2, 3, 2, 4]
    expected = [1, 2, 4, 6, 12, 24, 36, 48, 60]
    assert highly_composite_upto(60) == expected
