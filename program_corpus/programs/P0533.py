def lowest_common_ancestor(parent: dict[str, str], a: str, b: str) -> str:
    ancestors = set()
    node = a
    while node:
        ancestors.add(node)
        node = parent.get(node, "")
    node = b
    while node and node not in ancestors:
        node = parent.get(node, "")
    return node

if __name__ == "__main__":
    parent = {"b": "a", "c": "a", "d": "b", "e": "b"}
    assert lowest_common_ancestor(parent, "d", "e") == "b"
    assert lowest_common_ancestor(parent, "d", "c") == "a"
    assert lowest_common_ancestor(parent, "d", "x") == ""
