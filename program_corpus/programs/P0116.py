def count_array_inversions(items: list[int]) -> int:
    inversions = 0
    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            if items[i] > items[j]:
                inversions += 1
    return inversions

if __name__ == "__main__":
    assert count_array_inversions([2, 4, 1, 3, 5]) == 3
