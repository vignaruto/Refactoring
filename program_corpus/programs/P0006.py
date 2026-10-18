"""
Domain: Searching and Sorting
Task: Binary search over a pre-sorted integer array.
"""

from typing import List, Optional

def binary_search(arr: List[int], target: int) -> Optional[int]:
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None

if __name__ == "__main__":
    data = [10, 20, 30, 40, 50]
    assert binary_search(data, 30) == 2
    assert binary_search(data, 99) is None
