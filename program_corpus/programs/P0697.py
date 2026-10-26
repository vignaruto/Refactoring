def repeated_line_words(lines, min_length=3):
    hits = []
    for number, line in enumerate(lines, start=1):
        words = line.lower().split()
        for i in range(1, len(words)):
            word = words[i]
            if word == words[i - 1] and len(word) >= min_length and word.isalpha():
                hits.append((number, word))
    return hits

if __name__ == "__main__":
    lines = ["The the cat", "go go go", "a a"]
    hits = repeated_line_words(lines, 2)
    assert hits == [(1, "the"), (2, "go"), (2, "go")]
