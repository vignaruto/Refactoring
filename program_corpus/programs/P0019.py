"""
Domain: Searching and Sorting
Task: Run bubble sort on an array of floating point numbers.
"""

from typing import List

def bubble_sort(items: List[float]) -> List[float]:
    arr = list(items)
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

if __name__ == "__main__":
    unsorted = [64.0, 34.0, 25.0, 12.0, 22.0]
    assert bubble_sort(unsorted) == [12.0, 22.0, 25.0, 34.0, 64.0]
