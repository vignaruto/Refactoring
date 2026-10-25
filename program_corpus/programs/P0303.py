def lower_bound_index(items: list[int], target: int) -> int:
    left = 0
    right = len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left

if __name__ == "__main__":
    assert lower_bound_index([1, 2, 4, 4, 7], 4) == 2
    assert lower_bound_index([1, 2, 4, 4, 7], 5) == 4
    assert lower_bound_index([1, 2, 4], 9) == 3
