def prefix_flip_sort(values):
    items = list(values)
    flips = []
    for size in range(len(items), 1, -1):
        biggest = items.index(max(items[:size]))
        if biggest == size - 1:
            continue
        for k in (biggest + 1, size):
            if k > 1:
                items[:k] = items[:k][::-1]
                flips.append(k)
    return items, flips

if __name__ == "__main__":
    assert prefix_flip_sort([3, 1, 2]) == ([1, 2, 3], [3, 2])
    assert prefix_flip_sort([]) == ([], [])
