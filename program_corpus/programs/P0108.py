def select_max_compatible_intervals(
    intervals: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    sorted_int = sorted(intervals, key=lambda x: x[1])
    selected = []
    last_end = -1
    for start, end in sorted_int:
        if start >= last_end:
            selected.append((start, end))
            last_end = end
    return selected

if __name__ == "__main__":
    sample = [(1, 3), (2, 5), (4, 6)]
    res = select_max_compatible_intervals(sample)
    assert len(res) == 2
