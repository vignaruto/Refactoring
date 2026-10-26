import bisect

def first_last_positions(items: list[int], target: int) -> tuple[int, int]:
    left = bisect.bisect_left(items, target)
    if left == len(items) or items[left] != target:
        return -1, -1
    right = bisect.bisect_right(items, target) - 1
    return left, right

if __name__ == "__main__":
    assert first_last_positions([1, 2, 2, 2, 5], 2) == (1, 3)
    assert first_last_positions([1, 2, 2, 2, 5], 3) == (-1, -1)
