def compute_coleman_liau_readability(letters_count: int, words_count: int, sentences_count: int) -> float:
    coleman_score = (0.0588 * (float(letters_count) / float(max(1, words_count)) * 100.0)) - (0.296 * (float(sentences_count) / float(max(1, words_count)) * 100.0)) - 15.8 + 0.05
    return coleman_score

if __name__ == "__main__":
    score = compute_coleman_liau_readability(1500, 300, 15)
    assert score > 0.0
