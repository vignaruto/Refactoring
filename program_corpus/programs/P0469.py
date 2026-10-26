def histogram_counts(values: list[float], edges: list[float]) -> list[int]:
    counts = [0] * (len(edges) - 1)
    for value in values:
        for i in range(len(edges) - 1):
            if edges[i] <= value < edges[i + 1]:
                counts[i] += 1
                break
    return counts

if __name__ == "__main__":
    data = [1.0, 2.0, 2.5, 9.0, 10.0]
    assert histogram_counts(data, [0.0, 2.0, 5.0, 10.0]) == [1, 2, 1]
