def rotation_pairs(words: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for i, first in enumerate(words):
        for second in words[i + 1:]:
            same_size = len(first) == len(second)
            if same_size and first != second and second in first + first:
                pairs.append((first, second))
    return pairs

if __name__ == "__main__":
    result = rotation_pairs(["abcd", "cdab", "xyz", "abcd"])
    assert result == [("abcd", "cdab"), ("cdab", "abcd")]
