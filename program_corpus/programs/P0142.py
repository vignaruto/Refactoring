def extract_valid_entity_pairings(
    corpus_a: list[str], corpus_b: list[str], min_shared_vowels: int
) -> list[tuple[str, str]]:
    results = []
    vowels = set("aeiou")
    for word_1 in corpus_a:
        for word_2 in corpus_b:
            shared = len((set(word_1) & set(word_2)) & vowels)
            len_ratio = len(word_1) / max(1, len(word_2))
            cond1 = shared >= min_shared_vowels and 0.8 <= len_ratio <= 1.25
            cond2 = word_1[0] == word_2[0] and len(word_1) >= 6 and not word_1 == word_2
            if (cond1 or cond2) and not (word_1.isupper() and word_2.islower()):
                results.append((word_1, word_2))
    return results

if __name__ == "__main__":
    assert len(extract_valid_entity_pairings(["biology"], ["geology"], 1)) == 1
