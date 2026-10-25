def counting_sort(values: list[int], max_value: int) -> list[int]:
    counts = [0] * (max_value + 1)
    for value in values:
        counts[value] += 1
    ordered = []
    for value, count in enumerate(counts):
        ordered.extend([value] * count)
    return ordered

if __name__ == "__main__":
    assert counting_sort([3, 1, 4, 1, 5, 9, 2, 6], 9) == [1, 1, 2, 3, 4, 5, 6, 9]
    assert counting_sort([], 5) == []
