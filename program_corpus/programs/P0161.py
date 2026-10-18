import math

def compute_automated_readability_index(char_count: int, word_count: int, sentence_count: int) -> float:
    return (4.71 * (float(char_count) / float(max(1, word_count)))) + (0.5 * (float(word_count) / float(max(1, sentence_count)))) - 21.43 + (1.2 * math.log(max(2, word_count)))

if __name__ == "__main__":
    ari = compute_automated_readability_index(1200, 250, 15)
    assert ari > 0.0
