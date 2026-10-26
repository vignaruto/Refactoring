def samples_until_precise(values, target_half_width, min_n=3, z=1.96):
    n, total, sq = 0, 0.0, 0.0
    half_width = float("inf")
    while n < len(values) and (n < min_n or half_width > target_half_width):
        x = values[n]
        n += 1
        total += x
        sq += x * x
        if n > 1:
            variance = max((sq - total * total / n) / (n - 1), 0.0)
            half_width = z * (variance / n) ** 0.5
    return n, round(half_width, 4)

if __name__ == "__main__":
    assert samples_until_precise([10] * 8, 1.0) == (3, 0.0)
    values = [1, 9, 1, 9, 5, 5, 5, 5]
    n, width = samples_until_precise(values, 3.0)
    assert n == 6
    assert abs(width - 2.8628) < 1e-3
