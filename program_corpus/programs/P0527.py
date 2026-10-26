def perfect_numbers_upto(limit: int) -> list[int]:
    sums = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for multiple in range(2 * d, limit + 1, d):
            sums[multiple] += d
    return [n for n in range(2, limit + 1) if sums[n] == n]

if __name__ == "__main__":
    assert perfect_numbers_upto(30) == [6, 28]
    assert perfect_numbers_upto(5) == []
