import math
from collections import Counter

def trigram_cosine(a: str, b: str) -> float:
    grams_a = Counter(a.lower()[i:i + 3] for i in range(len(a) - 2))
    grams_b = Counter(b.lower()[i:i + 3] for i in range(len(b) - 2))
    dot = sum(grams_a[g] * grams_b[g] for g in grams_a)
    norm = math.sqrt(sum(v * v for v in grams_a.values())) * math.sqrt(sum(v * v for v in grams_b.values()))
    return round(dot / norm, 4) if norm else 0.0

if __name__ == "__main__":
    assert trigram_cosine("night", "night") == 1.0
    assert trigram_cosine("ab", "cd") == 0.0
