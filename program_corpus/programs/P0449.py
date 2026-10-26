def shingle_overlap_report(documents: dict[str, str], k: int, threshold: float) -> list[tuple[str, str, float]]:
    names = sorted(documents)
    shingles = {}
    for name in names:
        words = documents[name].lower().split()
        shingles[name] = {tuple(words[i:i + k]) for i in range(len(words) - k + 1)}
    report = []
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            a, b = shingles[first], shingles[second]
            jaccard = len(a & b) / len(a | b) if a | b else 0.0
            if jaccard >= threshold and len(a) >= 2 and len(b) >= 2:
                report.append((first, second, round(jaccard, 3)))
    return report

if __name__ == "__main__":
    docs = {
        "a": "the quick brown fox jumps",
        "b": "the quick brown fox sleeps",
        "c": "nothing alike here at all",
    }
    assert shingle_overlap_report(docs, 2, 0.4) == [("a", "b", 0.6)]
