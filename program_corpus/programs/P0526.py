def find_sublist_positions(haystack: list[int], pattern: list[int]) -> list[int]:
    positions = []
    width = len(pattern)
    start = 0
    while start + width <= len(haystack) and width:
        offset = 0
        while offset < width and haystack[start + offset] == pattern[offset]:
            offset += 1
        if offset == width:
            positions.append(start)
        start += 1
    return positions

if __name__ == "__main__":
    assert find_sublist_positions([1, 2, 1, 2, 1], [1, 2, 1]) == [0, 2]
    assert find_sublist_positions([3, 4], [5]) == []
    assert find_sublist_positions([3, 4], []) == []
