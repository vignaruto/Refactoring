def bin_counts(values, edges):
    counts = [0] * (len(edges) - 1)
    for v in values:
        for b in range(len(edges) - 1):
            if edges[b] <= v < edges[b + 1]:
                counts[b] += 1
                break
    return counts

if __name__ == "__main__":
    assert bin_counts([1, 2, 5, 7, 10], [0, 3, 6, 10]) == [2, 1, 1]
