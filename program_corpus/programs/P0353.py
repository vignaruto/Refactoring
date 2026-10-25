def exponential_search_index(items: list[int], target: int) -> int:
    if not items:
        return -1
    bound = 1
    while bound < len(items) and items[bound] < target:
        bound *= 2
    low = bound // 2
    high = min(bound, len(items) - 1)
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

if __name__ == "__main__":
    data = [1, 3, 5, 7, 9, 11, 13, 15, 17]
    assert exponential_search_index(data, 13) == 6
    assert exponential_search_index(data, 4) == -1
    assert exponential_search_index([], 4) == -1
