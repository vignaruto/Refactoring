def interpolation_search(arr: list[int], target: int) -> int:
    low = 0
    high = len(arr) - 1
    while low <= high and target >= arr[low] and target <= arr[high]:
        if low == high:
            if arr[low] == target:
                return low
            return -1
        pos = low + int(((float(high - low) / (arr[high] - arr[low])) * (target - arr[low])))
        if arr[pos] == target:
            return pos
        if arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    return -1

if __name__ == "__main__":
    data = [10, 20, 30, 40, 50, 60]
    assert interpolation_search(data, 40) == 3
