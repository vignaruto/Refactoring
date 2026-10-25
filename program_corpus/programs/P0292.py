def find_single_substitution_pairs(words: list[str], stop_words: set[str]) -> list[tuple[str, str]]:
    pairs = []
    unique = sorted(set(words))
    for i, first in enumerate(unique):
        for second in unique[i + 1:]:
            if len(first) != len(second):
                continue
            differences = 0
            for a, b in zip(first, second):
                if a != b:
                    differences += 1
            if differences == 1 and first not in stop_words and second not in stop_words:
                pairs.append((first, second))
    return pairs

if __name__ == "__main__":
    assert find_single_substitution_pairs(["cat", "cot", "cog", "dog", "the", "tho"], {"the"}) == [("cat", "cot"), ("cog", "cot"), ("cog", "dog")]
