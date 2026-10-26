def bucket_sort_range(values, buckets=5):
    if not values:
        return []
    low, high = min(values), max(values)
    bins = [[] for _ in range(buckets)]
    for v in values:
        slot = min(int((v - low) / (high - low) * buckets), buckets - 1) if high > low else 0
        bins[slot].append(v)
    result = []
    for b in bins:
        for i in range(1, len(b)):
            key, j = b[i], i - 1
            while j >= 0 and b[j] > key:
                b[j + 1] = b[j]
                j -= 1
            b[j + 1] = key
        result.extend(b)
    return result

if __name__ == "__main__":
    data = [0.42, 4.2, 1.5, 3.3, 0.1, 2.2, 4.2]
    assert bucket_sort_range(data) == sorted(data)
    assert bucket_sort_range([7, 7]) == [7, 7]
    assert bucket_sort_range([]) == []
