def invert_multimap(mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    inverted = {}
    for key, values in mapping.items():
        for value in values:
            if key not in inverted.get(value, []):
                inverted.setdefault(value, []).append(key)
    pairs = sorted(inverted.items())
    return {v: sorted(ks) for v, ks in pairs}

if __name__ == "__main__":
    data = {"b": ["x"], "a": ["x", "y", "x"]}
    assert invert_multimap(data) == {"x": ["a", "b"], "y": ["a"]}
