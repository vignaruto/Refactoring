def gunning_fog_index(text: str) -> float:
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    words = [w.strip(".,!?;:").lower() for w in text.split() if w.strip(".,!?;:")]
    complex_words = sum(1 for w in words if sum(1 for ch in w if ch in "aeiouy") >= 3)
    fog = 0.4 * ((len(words) / sentences) + 100.0 * (complex_words / max(1, len(words))))
    return round(fog, 2)

if __name__ == "__main__":
    assert gunning_fog_index("The cat sat. It was happy.") == 1.2
