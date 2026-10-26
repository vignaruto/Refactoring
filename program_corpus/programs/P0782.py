def pairwise_dot(vectors):
    names = sorted(vectors)
    result = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            small, large = sorted((vectors[a], vectors[b]), key=len)
            result[(a, b)] = sum(weight * large.get(term, 0) for term, weight in small.items())
    return result

if __name__ == "__main__":
    vectors = {"d1": {"x": 1, "y": 2}, "d2": {"y": 3}}
    vectors["d3"] = {"z": 1}
    result = pairwise_dot(vectors)
    assert result == {("d1", "d2"): 6, ("d1", "d3"): 0, ("d2", "d3"): 0}
