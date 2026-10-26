def aligned_matches(rows, min_shared=2):
    matches = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            shared = sum(1 for a, b in zip(rows[i], rows[j]) if a == b)
            if shared >= min_shared and len(rows[i]) == len(rows[j]) and rows[i] != rows[j]:
                matches.append((i, j, shared))
    return matches

if __name__ == "__main__":
    rows = [(1, 2, 3), (1, 2, 4), (1, 2, 3), (9, 9)]
    assert aligned_matches(rows) == [(0, 1, 2), (1, 2, 2)]
