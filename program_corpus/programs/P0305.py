def invert_unique_mapping(mapping: dict[str, int]) -> dict[int, str]:
    inverted: dict[int, str] = {}
    for key, value in mapping.items():
        if value in inverted:
            raise ValueError("duplicate value in mapping")
        inverted[value] = key
    return inverted

if __name__ == "__main__":
    assert invert_unique_mapping({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert_unique_mapping({}) == {}
