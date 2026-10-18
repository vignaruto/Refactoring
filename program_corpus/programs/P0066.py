from typing import List

def shell_sort_integers(items: List[int]) -> List[int]:
    arr = list(items)
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr

if __name__ == "__main__":
    assert shell_sort_integers([9, 8, 3, 7, 5, 6, 4, 1]) == [1, 3, 4, 5, 6, 7, 8, 9]
