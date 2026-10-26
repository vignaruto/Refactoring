def group_by_initial(lists, banned, min_len):
    groups = {}
    for words in lists:
        for word in words:
            w = word.strip().lower()
            if w and len(w) >= min_len and w not in banned and w not in groups.get(w[0], []):
                groups.setdefault(w[0], []).append(w)
    return groups

if __name__ == "__main__":
    lists = [["Apple", "ant"], ["apple ", "bee", "be"]]
    assert group_by_initial(lists, {"ant"}, 3) == {"a": ["apple"], "b": ["bee"]}
