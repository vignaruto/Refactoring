def is_valid_bst(tree: dict[int, tuple[int | None, int | None]], node: int | None, low: float = float("-inf"), high: float = float("inf")) -> bool:
    if node is None:
        return True
    if node <= low or node >= high or node not in tree:
        return False
    left, right = tree[node]
    left_ok = is_valid_bst(tree, left, low, node)
    return left_ok and is_valid_bst(tree, right, node, high)

if __name__ == "__main__":
    tree = {5: (3, 8), 3: (None, None), 8: (None, None)}
    assert is_valid_bst(tree, 5) is True
    bad = dict(tree)
    bad[3] = (None, 6)
    bad[6] = (None, None)
    assert is_valid_bst(bad, 5) is False
