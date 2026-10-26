from collections import Counter

def top_k_frequent(items: list[str], k: int) -> list[str]:
    counts = Counter(items)
    ranked = sorted(counts, key=lambda w: (-counts[w], w))
    return ranked[:k]

if __name__ == "__main__":
    words = ["b", "a", "c", "b", "a", "d"]
    assert top_k_frequent(words, 2) == ["a", "b"]
