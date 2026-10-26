def repeated_phrase_report(sentences: list[str], n: int, stopwords: set[str]) -> list[str]:
    counts = {}
    for sentence in sentences:
        words = sentence.lower().split()
        for i in range(len(words) - n + 1):
            gram = words[i:i + n]
            if gram[0] not in stopwords and gram[-1] not in stopwords and len(set(gram)) == n:
                key = " ".join(gram)
                counts[key] = counts.get(key, 0) + 1
    report = [f"{phrase} x{count}" for phrase, count in sorted(counts.items()) if count > 1]
    return report

if __name__ == "__main__":
    text = ["the red fox runs", "a red fox sleeps"]
    text.append("red fox red fox")
    assert repeated_phrase_report(text, 2, {"the", "a"}) == ["red fox x4"]
