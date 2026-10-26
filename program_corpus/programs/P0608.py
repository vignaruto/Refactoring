def gallop_lower_bound(values, target):
    bound = 1
    while bound < len(values) and values[bound] < target and bound < 1 << 30:
        bound *= 2
    lo, hi = bound // 2, min(bound, len(values))
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

if __name__ == "__main__":
    nums = [1, 3, 5, 7, 9, 11]
    assert gallop_lower_bound(nums, 6) == 3
    assert gallop_lower_bound(nums, 0) == 0
    assert gallop_lower_bound(nums, 12) == 6
    assert gallop_lower_bound([], 5) == 0
