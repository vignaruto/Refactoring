def cycle_sort_writes(values: list[int]) -> tuple[list[int], int]:
    data = list(values)
    writes = 0
    for start in range(len(data) - 1):
        item = data[start]
        pos = start
        for i in range(start + 1, len(data)):
            if data[i] < item:
                pos += 1
        if pos == start:
            continue
        while item == data[pos]:
            pos += 1
        data[pos], item = item, data[pos]
        writes += 1
        while pos != start:
            pos = start
            for i in range(start + 1, len(data)):
                if data[i] < item:
                    pos += 1
            while item == data[pos]:
                pos += 1
            data[pos], item = item, data[pos]
            writes += 1
    return data, writes

if __name__ == "__main__":
    assert cycle_sort_writes([5, 2, 4, 2, 1])[0] == [1, 2, 2, 4, 5]
    assert cycle_sort_writes([1, 2, 3]) == ([1, 2, 3], 0)
