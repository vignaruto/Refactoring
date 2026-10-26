def rising_triples(values, max_gap):
    count = 0
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            if values[j] <= values[i] or values[j] - values[i] > max_gap:
                continue
            for k in range(j + 1, n):
                if values[i] < values[j] < values[k] and values[k] - values[j] <= max_gap:
                    count += 1
    return count

if __name__ == "__main__":
    assert rising_triples([1, 2, 3, 4], 1) == 2
    assert rising_triples([1, 2, 3, 4], 5) == 4
    assert rising_triples([3, 2, 1], 5) == 0
