def cocktail_shaker_sort(items: list[int]) -> list[int]:
    arr = list(items)
    n = len(arr)
    swapped = True
    start = 0
    end = n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        start += 1
    return arr

if __name__ == "__main__":
    assert cocktail_shaker_sort([5, 1, 4, 2, 8, 0, 2]) == [0, 1, 2, 2, 4, 5, 8]
