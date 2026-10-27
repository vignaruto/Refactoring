def comb_sort_values(values: list[int]) -> list[int]:
    arr = list(values)
    gap = len(arr)
    swapped = True
    while gap > 1 or swapped:
        gap = max(1, int(gap / 1.3))
        swapped = False
        for i in range(len(arr) - gap):
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                swapped = True
    return arr

if __name__ == "__main__":
    assert comb_sort_values([8, 4, 1, 56, 3, -44, 23]) == [-44, 1, 3, 4, 8, 23, 56]
    assert comb_sort_values([]) == []
