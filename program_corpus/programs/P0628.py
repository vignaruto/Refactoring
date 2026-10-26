def doubled_letter_counts(lines, min_len):
    counts = {}
    for number, line in enumerate(lines, start=1):
        words = line.lower().split()
        for position, raw in enumerate(words):
            w = raw.strip(".,;:!?")
            doubled = any(a == b for a, b in zip(w, w[1:]))
            if doubled and len(w) >= min_len and w.isalpha():
                counts.setdefault(w, []).append((number, position))
    return counts

if __name__ == "__main__":
    lines = ["Look at the moon.", "Good food, cool moon"]
    found = doubled_letter_counts(lines, 4)
    assert found["moon"] == [(1, 3), (2, 3)]
    assert sorted(found) == ["cool", "food", "good", "look", "moon"]
