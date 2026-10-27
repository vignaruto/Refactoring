def pancake_sort(items: list[int]) -> list[int]:
    arr = list(items)
    curr_size = len(arr)
    while curr_size > 1:
        max_idx = 0
        for i in range(1, curr_size):
            if arr[i] > arr[max_idx]:
                max_idx = i
        if max_idx != curr_size - 1:
            arr[:max_idx + 1] = reversed(arr[:max_idx + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
        curr_size -= 1
    return arr

if __name__ == "__main__":
    assert pancake_sort([3, 2, 4, 1]) == [1, 2, 3, 4]
