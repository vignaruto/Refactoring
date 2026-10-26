def frequent_letter_pairs(words: list[str], least: int) -> list[str]:
    counts = {}
    for word in words:
        for i in range(len(word) - 1):
            a, b = word[i], word[i + 1]
            if a.isalpha() and b.isalpha() and a != b:
                pair = (a + b).lower()
                counts[pair] = counts.get(pair, 0) + 1
    return sorted(p for p, n in counts.items() if n >= least)

if __name__ == "__main__":
    words = ["hello", "yellow", "mellow"]
    assert frequent_letter_pairs(words, 3) == ["el", "lo"]
    assert frequent_letter_pairs(["a1b"], 1) == []
