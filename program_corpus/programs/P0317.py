def character_bigram_counts(words: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in words:
        cleaned = word.lower()
        for idx in range(len(cleaned) - 1):
            pair = cleaned[idx:idx + 2]
            counts[pair] = counts.get(pair, 0) + 1
    return counts

if __name__ == "__main__":
    assert character_bigram_counts(["banana"]) == {"ba": 1, "an": 2, "na": 2}
    assert character_bigram_counts(["a", ""]) == {}
