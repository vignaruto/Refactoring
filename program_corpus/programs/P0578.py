def complementary_pairs(scores, total):
    names = sorted(scores)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if scores[a] + scores[b] == total and scores[a] >= 0 and scores[b] >= 0:
                pairs.append((a, b))
    return pairs

if __name__ == "__main__":
    scores = {"x": 3, "y": 7, "z": 5, "w": -2, "v": 12}
    assert complementary_pairs(scores, 10) == [("x", "y")]
