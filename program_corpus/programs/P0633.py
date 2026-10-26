def longest_rising_runs(lists):
    results = []
    for seq in lists:
        best_start, best_len = 0, 0
        start = 0
        for i in range(1, len(seq) + 1):
            if i == len(seq) or seq[i] <= seq[i - 1]:
                if i - start > best_len:
                    best_start, best_len = start, i - start
                start = i
        results.append((best_start, best_len))
    return results

if __name__ == "__main__":
    runs = longest_rising_runs([[1, 2, 3, 1, 2], [5, 4], []])
    assert runs == [(0, 3), (0, 1), (0, 0)]
