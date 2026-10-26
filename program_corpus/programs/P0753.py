def three_way_partition(values, pivot):
    items = list(values)
    low, mid, high = 0, 0, len(items) - 1
    while mid <= high:
        if items[mid] < pivot:
            items[low], items[mid] = items[mid], items[low]
            low += 1
            mid += 1
        elif items[mid] > pivot:
            items[mid], items[high] = items[high], items[mid]
            high -= 1
        else:
            mid += 1
    return items, low, high

if __name__ == "__main__":
    values = [3, 1, 2, 3, 5, 0]
    items, low, high = three_way_partition(values, 3)
    assert all(v < 3 for v in items[:low])
    assert items[low:high + 1] == [3, 3]
    assert all(v > 3 for v in items[high + 1:])
