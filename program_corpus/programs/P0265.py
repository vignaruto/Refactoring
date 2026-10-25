def insertion_sort(values: list[int]) -> list[int]:
    items = list(values)
    for index in range(1, len(items)):
        current = items[index]
        position = index - 1
        while position >= 0 and items[position] > current:
            items[position + 1] = items[position]
            position -= 1
        items[position + 1] = current
    return items

if __name__ == "__main__":
    assert insertion_sort([5, 2, 4, 6, 1, 3]) == [1, 2, 3, 4, 5, 6]
    assert insertion_sort([]) == []
