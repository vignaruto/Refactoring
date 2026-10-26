def balanced_height(tree, node):
    if node is None:
        return 0
    left, right = tree.get(node, (None, None))
    lh = balanced_height(tree, left)
    rh = balanced_height(tree, right)
    if lh < 0 or rh < 0 or abs(lh - rh) > 1:
        return -1
    return 1 + max(lh, rh)

if __name__ == "__main__":
    tree = {"a": ("b", "c"), "b": ("d", None)}
    assert balanced_height(tree, "a") == 3
    chain = {"a": ("b", None), "b": ("c", None)}
    assert balanced_height(chain, "a") == -1
