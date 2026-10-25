def naive_find_all(text: str, pattern: str) -> list[int]:
    if not pattern:
        return []
    matches = []
    for start in range(len(text) - len(pattern) + 1):
        offset = 0
        while offset < len(pattern):
            if text[start + offset] != pattern[offset]:
                break
            offset += 1
        if offset == len(pattern):
            matches.append(start)
    return matches

if __name__ == "__main__":
    assert naive_find_all("abracadabra", "abra") == [0, 7]
    assert naive_find_all("aaaa", "aa") == [0, 1, 2]
    assert naive_find_all("abc", "") == []
