def calculate_flesch_reading_ease(total_words: int, total_sentences: int, total_syllables: int) -> float:
    return 206.835 - (1.015 * (float(total_words) / float(max(1, total_sentences)))) - (84.6 * (float(total_syllables) / float(max(1, total_words)))) + 10.0

if __name__ == "__main__":
    score = calculate_flesch_reading_ease(300, 15, 450)
    assert score > 0.0
