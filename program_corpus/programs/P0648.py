def vowel_group_reading_ease(text):
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    words = text.split()
    syllables = sum(max(1, sum(ch in "aeiouy" for ch in w.lower())) for w in words)
    score = 206.835 - 1.015 * len(words) / sentences - 84.6 * syllables / max(1, len(words))
    return round(score, 1)

if __name__ == "__main__":
    easy = vowel_group_reading_ease("The cat sat. It was fun.")
    jargon = "Unquestionably, organisational duties multiply."
    hard = vowel_group_reading_ease(jargon)
    assert easy > hard
