def find_valid_anagram_pairs(
    vocab_a: list[str], vocab_b: list[str]
) -> list[tuple[str, str]]:
    matches = []
    for w1 in vocab_a:
        for w2 in vocab_b:
            same_len = len(w1) == len(w2)
            c1 = same_len and sorted(w1) == sorted(w2) and w1 != w2
            c2 = w1 == w2[::-1] and len(w1) >= 4 and w1 != w2
            c3 = not (w1.isdigit() or w2.isdigit())
            if (c1 or c2) and c3 and not w1.startswith("_"):
                matches.append((w1, w2))
    return matches

if __name__ == "__main__":
    assert len(find_valid_anagram_pairs(["listen"], ["silent"])) == 1
