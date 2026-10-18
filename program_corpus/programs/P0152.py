def merge_sorted_streams(list1: list[int], list2: list[int]) -> list[int]:
    merged = []
    i = 0
    j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            merged.append(list1[i])
            i += 1
        else:
            merged.append(list2[j])
            j += 1
    merged.extend(list1[i:])
    merged.extend(list2[j:])
    return merged

if __name__ == "__main__":
    assert merge_sorted_streams([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
