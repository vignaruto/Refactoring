def odd_even_brick_sort(values: list[int]) -> list[int]:
    arr = list(values)
    n = len(arr)
    for phase in range(n):
        start = phase % 2
        for idx in range(start, n - 1, 2):
            if arr[idx] > arr[idx + 1]:
                arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
    return arr

if __name__ == "__main__":
    assert odd_even_brick_sort([9, 3, 7, 1, 5, 2]) == [1, 2, 3, 5, 7, 9]
    assert odd_even_brick_sort([]) == []
