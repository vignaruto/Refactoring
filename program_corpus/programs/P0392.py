def palindrome_join_pairs(words: list[str], min_len: int) -> list[tuple[int, int]]:
    pairs = []
    for i, first in enumerate(words):
        for j, second in enumerate(words):
            joined = first + second
            if i != j and len(joined) >= min_len and joined == joined[::-1]:
                pairs.append((i, j))
    return pairs

if __name__ == "__main__":
    assert palindrome_join_pairs(["ab", "ba", "x"], 2) == [(0, 1), (1, 0)]
