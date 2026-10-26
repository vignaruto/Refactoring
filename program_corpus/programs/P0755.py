def tree_height(children: dict, node) -> int:
    kids = children.get(node, [])
    if not kids:
        return 0
    return 1 + max(tree_height(children, k) for k in kids)


def leaf_names(children: dict, node) -> list:
    kids = children.get(node, [])
    if not kids:
        return [node]
    leaves = []
    for kid in kids:
        leaves.extend(leaf_names(children, kid))
    return leaves


if __name__ == "__main__":
    children = {"r": ["a", "b"], "a": ["c", "d"]}
    assert tree_height(children, "r") == 2
    assert leaf_names(children, "r") == ["c", "d", "b"]
