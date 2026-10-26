def find_in_rotated(values, target):
    lo, hi = 0, len(values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if values[mid] == target:
            return mid
        if values[lo] <= values[mid] and values[lo] <= target < values[mid]:
            hi = mid - 1
        elif values[lo] > values[mid] and values[mid] < target <= values[hi]:
            lo = mid + 1
        elif values[lo] <= values[mid]:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

if __name__ == "__main__":
    rotated = [4, 5, 6, 7, 0, 1, 2]
    assert find_in_rotated(rotated, 0) == 4
    assert find_in_rotated(rotated, 5) == 1
    assert find_in_rotated(rotated, 3) == -1
