def scan_merge_sorted(lists):
    heads = [0] * len(lists)
    merged = []
    total = sum(len(lst) for lst in lists)
    while len(merged) < total:
        best = None
        for i, lst in enumerate(lists):
            if heads[i] >= len(lst):
                continue
            if best is None or lst[heads[i]] < lists[best][heads[best]]:
                best = i
        merged.append(lists[best][heads[best]])
        heads[best] += 1
    return merged

if __name__ == "__main__":
    parts = [[1, 4, 9], [2, 3], [], [5]]
    assert scan_merge_sorted(parts) == [1, 2, 3, 4, 5, 9]
