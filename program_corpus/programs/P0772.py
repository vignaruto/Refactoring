def first_close_duplicate(values, k, ignore=()):
    last_seen = {}
    for i, v in enumerate(values):
        if v not in ignore and v in last_seen and i - last_seen[v] <= k:
            return i
        last_seen[v] = i
    return -1

if __name__ == "__main__":
    values = [1, 2, 3, 1, 2]
    assert first_close_duplicate(values, 2) == -1
    assert first_close_duplicate(values, 3) == 3
    assert first_close_duplicate(values, 3, {1}) == 4
