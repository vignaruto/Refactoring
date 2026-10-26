def rotation_point(values):
    lo, hi = 0, len(values) - 1
    while lo < hi and values and values[lo] > values[hi]:
        mid = (lo + hi) // 2
        if values[mid] > values[hi]:
            lo = mid + 1
        else:
            hi = mid
    return lo

if __name__ == "__main__":
    assert rotation_point([4, 5, 6, 1, 2, 3]) == 3
    assert rotation_point([1, 2, 3]) == 0
    assert rotation_point([2, 1]) == 1
    assert rotation_point([]) == 0
