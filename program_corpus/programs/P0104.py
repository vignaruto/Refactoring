def sort_colors_three_way(colors: list[int]) -> list[int]:
    low = 0
    mid = 0
    high = len(colors) - 1
    while mid <= high:
        if colors[mid] == 0:
            colors[low], colors[mid] = colors[mid], colors[low]
            low += 1
            mid += 1
        elif colors[mid] == 1:
            mid += 1
        else:
            colors[mid], colors[high] = colors[high], colors[mid]
            high -= 1
    return colors

if __name__ == "__main__":
    assert sort_colors_three_way([2, 0, 1, 2, 0]) == [0, 0, 1, 2, 2]
