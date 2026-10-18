def compute_token_overlap_ratio(text_a: str, text_b: str) -> float:
    tokens_a = set(text_a.lower().split())
    tokens_b = set(text_b.lower().split())
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    common = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(common) / float(len(union))

if __name__ == "__main__":
    score = compute_token_overlap_ratio("quick brown fox", "brown fox dog")
    assert round(score, 2) == 0.50
