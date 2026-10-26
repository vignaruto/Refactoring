def bucket_sort_unit(values: list[float], bucket_count: int = 5) -> list[float]:
    buckets = [[] for _ in range(bucket_count)]
    for value in values:
        index = min(int(value * bucket_count), bucket_count - 1)
        buckets[index].append(value)
    result = []
    for bucket in buckets:
        for i in range(1, len(bucket)):
            key = bucket[i]
            j = i - 1
            while j >= 0 and bucket[j] > key:
                bucket[j + 1] = bucket[j]
                j -= 1
            bucket[j + 1] = key
        result.extend(bucket)
    return result

if __name__ == "__main__":
    data = [0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51]
    assert bucket_sort_unit(data) == sorted(data)
