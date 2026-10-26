def tag_similarity(tags_a: set, tags_b: set) -> tuple:
    if not tags_a or not tags_b:
        return 0.0, 0.0
    shared = len(tags_a & tags_b)
    union = len(tags_a | tags_b)
    dice = 2 * shared / (len(tags_a) + len(tags_b))
    blended = (shared / union + shared / min(len(tags_a), len(tags_b)) + dice) / 3
    jaccard = shared / union
    return round(jaccard, 3), round(blended, 3)


if __name__ == "__main__":
    assert tag_similarity({"x", "y"}, {"y", "z"}) == (0.333, 0.444)
    assert tag_similarity(set(), {"y"}) == (0.0, 0.0)
