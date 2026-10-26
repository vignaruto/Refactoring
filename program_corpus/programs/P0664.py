def transpose_mapping(outer):
    flipped = {}
    for key, inner in outer.items():
        for sub_key, value in inner.items():
            flipped.setdefault(sub_key, {})[key] = value
    return flipped

if __name__ == "__main__":
    scores = {"a": {"x": 1, "y": 2}, "b": {"x": 3}}
    flipped = transpose_mapping(scores)
    assert flipped == {"x": {"a": 1, "b": 3}, "y": {"a": 2}}
