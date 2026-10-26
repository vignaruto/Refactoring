def merge_by_head_scan(lists):
    heads = [0] * len(lists)
    merged = []
    while True:
        best = -1
        for i, seq in enumerate(lists):
            if heads[i] < len(seq) and (best == -1 or seq[heads[i]] < lists[best][heads[best]]):
                best = i
        if best == -1:
            return merged
        merged.append(lists[best][heads[best]])
        heads[best] += 1

if __name__ == "__main__":
    assert merge_by_head_scan([[1, 4, 9], [2, 3], [], [5]]) == [1, 2, 3, 4, 5, 9]
    assert merge_by_head_scan([]) == []
