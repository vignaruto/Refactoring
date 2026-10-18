"""
Domain: Searching and Sorting
Task: Run selection sort to organize integers in ascending order.
"""

from typing import List, Tuple

def selection_sort(items: List[int]) -> List[int]:
    arr = list(items)
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

if __name__ == "__main__":
    assert selection_sort([29, 10, 14, 37, 13]) == [10, 13, 14, 29, 37]
