def acronym_expansions(words: list[str], acronyms: list[str]) -> dict[str, str]:
    found = {}
    for acronym in acronyms:
        size = len(acronym)
        for start in range(len(words) - size + 1):
            window = words[start:start + size]
            initials = "".join(w[0].upper() for w in window if w)
            long_words = all(len(w) > 1 for w in window)
            if initials == acronym and acronym not in found and long_words:
                found[acronym] = " ".join(window)
    return found

if __name__ == "__main__":
    words = "the world health organization met".split()
    expected = {"WHO": "world health organization"}
    assert acronym_expansions(words, ["WHO", "XYZ"]) == expected
