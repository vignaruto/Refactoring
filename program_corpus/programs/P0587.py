def flatten_and_count(nested):
    counts = {}
    for group in nested:
        for item in group:
            counts[item] = counts.get(item, 0) + 1
    return sorted(counts.items(), key=lambda p: (-p[1], p[0]))

if __name__ == "__main__":
    groups = [["a", "b"], ["b"], ["c", "b", "a"]]
    assert flatten_and_count(groups) == [("b", 3), ("a", 2), ("c", 1)]
