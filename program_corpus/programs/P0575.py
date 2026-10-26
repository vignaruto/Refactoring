def palindromic_words(sentences, min_len):
    found = []
    for sentence in sentences:
        for raw in sentence.split():
            w = raw.strip(".,!?").lower()
            if len(w) >= min_len and w == w[::-1] and w.isalpha() and w not in found:
                found.append(w)
    return found

if __name__ == "__main__":
    text = ["Anna saw a racecar.", "Wow, level up!"]
    assert palindromic_words(text, 3) == ["anna", "racecar", "wow", "level"]
    assert palindromic_words(text, 6) == ["racecar"]
