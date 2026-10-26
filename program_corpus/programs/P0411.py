import string

def lexical_richness(text: str) -> tuple[float, float]:
    tokens = [t.strip(string.punctuation).lower() for t in text.split() if t.strip(string.punctuation)]
    if not tokens:
        return 0.0, 0.0
    frequencies = {token: tokens.count(token) for token in set(tokens)}
    hapax_ratio = sum(1 for count in frequencies.values() if count == 1) / len(frequencies)
    return round(len(frequencies) / len(tokens), 4), round(hapax_ratio, 4)

if __name__ == "__main__":
    assert lexical_richness("the cat and the hat") == (0.8, 0.75)
    assert lexical_richness("...") == (0.0, 0.0)
