def char_ngram_profile(text, max_n):
    profile = {}
    cleaned = text.lower()
    for n in range(1, max_n + 1):
        for i in range(len(cleaned) - n + 1):
            gram = cleaned[i:i + n]
            profile[gram] = profile.get(gram, 0) + 1
    return profile

if __name__ == "__main__":
    assert char_ngram_profile("abab", 2) == {"a": 2, "b": 2, "ab": 2, "ba": 1}
