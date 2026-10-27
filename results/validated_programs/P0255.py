def group_words_by_initial(words: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for word in words:
        cleaned = word.strip().lower()
        if not cleaned:
            continue
        groups.setdefault(cleaned[0], []).append(cleaned)
    return groups

if __name__ == "__main__":
    assert group_words_by_initial(["Apple", "avocado", "Banana", " "]) == {"a": ["apple", "avocado"], "b": ["banana"]}
    assert group_words_by_initial([]) == {}
