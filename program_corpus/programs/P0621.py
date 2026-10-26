def close_pairs(values, max_gap):
    ordered = sorted(values)
    pairs = []
    for i in range(len(ordered)):
        j = i + 1
        while j < len(ordered) and ordered[j] - ordered[i] <= max_gap and ordered[j] != ordered[i]:
            pairs.append((ordered[i], ordered[j]))
            j += 1
    return pairs

if __name__ == "__main__":
    assert close_pairs([1, 4, 2, 9], 2) == [(1, 2), (2, 4)]
    assert close_pairs([], 3) == []
