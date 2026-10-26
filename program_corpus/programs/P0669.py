def is_search_tree(tree: dict, root) -> bool:
    visited = set()
    stack = [(root, float("-inf"), float("inf"))]
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        value, left, right = tree[node]
        if not low < value < high or node in visited:
            return False
        visited.add(node)
        stack.append((left, low, value))
        stack.append((right, value, high))
    return True


if __name__ == "__main__":
    good = {"r": (5, "a", "b")}
    good["a"] = (3, None, None)
    good["b"] = (8, None, None)
    bad = {"r": (5, "a", None), "a": (7, None, None)}
    assert is_search_tree(good, "r")
    assert not is_search_tree(bad, "r")
