def longest_shared_prefix(words: list[str]) -> str:
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        length = 0
        for a, b in zip(prefix, word):
            if a != b:
                break
            length += 1
        prefix = prefix[:length]
    return prefix

if __name__ == "__main__":
    assert longest_shared_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_shared_prefix(["dog", "car"]) == ""
