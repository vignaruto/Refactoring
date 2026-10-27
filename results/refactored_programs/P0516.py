def qualifying_leaf_paths(tree: dict[str, list[str]], weight: dict[str, int], root: str, low: int, high: int) -> list[str]:
    found = []
    stack = [(root, weight[root])]
    while stack:
        node, total = stack.pop()
        children = tree.get(node, [])
        condition = not children and low <= total <= high
        if condition:
            condition = node != root
        if condition:
            found.append(node)
        for child in children:
            stack.append((child, total + weight[child]))
    return sorted(found)

if __name__ == "__main__":
    t = {"r": ["a", "b"], "a": ["c"]}
    w = {"r": 1, "a": 2, "b": 9, "c": 3}
    assert qualifying_leaf_paths(t, w, "r", 5, 8) == ["c"]
    assert qualifying_leaf_paths(t, w, "r", 5, 10) == ["b", "c"]
