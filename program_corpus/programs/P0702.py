def transition_counts(words):
    table = {}
    for word in words:
        for first, second in zip(word, word[1:]):
            row = table.setdefault(first, {})
            row[second] = row.get(second, 0) + 1
    return table

def likeliest_next(table, ch):
    row = table.get(ch, {})
    return max(sorted(row), key=row.get) if row else None

if __name__ == "__main__":
    table = transition_counts(["abab", "ac"])
    assert table == {"a": {"b": 2, "c": 1}, "b": {"a": 1}}
    assert likeliest_next(table, "a") == "b"
    assert likeliest_next(table, "z") is None
