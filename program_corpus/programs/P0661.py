def letter_positions(words):
    index = {}
    for w_idx, word in enumerate(words):
        for c_idx, ch in enumerate(word):
            index.setdefault(ch, []).append((w_idx, c_idx))
    return index

def letters_in_every_word(index, word_count):
    shared = []
    for ch, spots in index.items():
        if len({w for w, _ in spots}) == word_count:
            shared.append(ch)
    return sorted(shared)

if __name__ == "__main__":
    idx = letter_positions(["ab", "ba"])
    assert idx == {"a": [(0, 0), (1, 1)], "b": [(0, 1), (1, 0)]}
    words = ["stone", "notes", "tone"]
    assert letters_in_every_word(letter_positions(words), 3) == list("enot")
