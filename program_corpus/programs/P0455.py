def tree_max_depth(children: dict[str, list[str]], node: str) -> int:
    kids = children.get(node, [])
    if not kids:
        return 1
    depths = [tree_max_depth(children, kid) for kid in kids]
    return 1 + max(depths)

if __name__ == "__main__":
    tree = {"a": ["b", "c"], "b": ["d"]}
    assert tree_max_depth(tree, "a") == 3
    assert tree_max_depth({}, "x") == 1
