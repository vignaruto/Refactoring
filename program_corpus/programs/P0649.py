def weighted_grid_sum(n, m, threshold):
    total = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if i % 2 == 0 and j % 3 != 0 and i * j <= threshold:
                total += i * j * 0.5 + (i - j) * (i - j) * 0.25 + 1.0 / (i + j)
    return round(total, 4)

if __name__ == "__main__":
    assert weighted_grid_sum(2, 2, 10) == 3.8333
    assert weighted_grid_sum(1, 5, 10) == 0.0
