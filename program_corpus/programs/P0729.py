def window_pairs(values, low, high, max_distance):
    pairs = []
    for i in range(len(values)):
        for j in range(i + 1, min(i + max_distance + 1, len(values))):
            total = values[i] + values[j]
            if low <= total <= high and values[i] != values[j]:
                pairs.append((i, j))
    return pairs

if __name__ == "__main__":
    assert window_pairs([1, 4, 2, 3], 4, 5, 2) == [(0, 1), (2, 3)]
    assert window_pairs([2, 2], 4, 4, 1) == []
