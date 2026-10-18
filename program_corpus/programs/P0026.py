"""
Domain: Searching and Sorting
Task: Count common elements across three sorted integer arrays.
"""

from typing import List

def count_three_way_intersections(list_a: List[int], list_b: List[int], list_c: List[int]) -> int:
    matches = 0
    for a in list_a:
        for b in list_b:
            for c in list_c:
                if a == b == c:
                    matches += 1
    return matches

if __name__ == "__main__":
    assert count_three_way_intersections([1, 2], [2, 3], [2, 4]) == 1
