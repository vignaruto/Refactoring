"""
Domain: Lists, Tuples, Dictionaries, and Sets
Task: Partition an integer list into even and odd buckets.
"""

from typing import List, Dict

def partition_evens_odds(numbers: List[int]) -> Dict[str, List[int]]:
    result = {"even": [], "odd": []}
    for num in numbers:
        if num % 2 == 0:
            result["even"].append(num)
        else:
            result["odd"].append(num)
    return result

if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5, 6]
    res = partition_evens_odds(nums)
    assert res["even"] == [2, 4, 6]
    assert res["odd"] == [1, 3, 5]
