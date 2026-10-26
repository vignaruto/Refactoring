def first_free_gap(busy: list[tuple[int, int]], day_start: int, day_end: int, length: int) -> int:
    cursor = day_start
    for start, end in sorted(busy):
        if start - cursor >= length:
            return cursor
        cursor = max(cursor, end)
    return cursor if day_end - cursor >= length else -1

if __name__ == "__main__":
    busy = [(9, 10), (10, 12), (13, 14)]
    assert first_free_gap(busy, 9, 17, 1) == 12
    assert first_free_gap(busy, 9, 17, 2) == 14
    assert first_free_gap(busy, 9, 17, 4) == -1
