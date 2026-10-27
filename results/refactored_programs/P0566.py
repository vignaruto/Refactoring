def check_search_tree_order(tree, node, low=None, high=None):
    if node is None:
        return True
    value, left, right = tree[node]
    condition = value is None
    if not condition:
        condition = low is not None and value <= low
    if not condition:
        condition = high is not None and value >= high
    if condition:
        return False
    if not check_search_tree_order(tree, left, low, value):
        return False
    return check_search_tree_order(tree, right, value, high)

if __name__ == "__main__":
    t = {"r": (8, "a", "b"), "a": (3, None, None)}
    t["b"] = (10, "c", None)
    t["c"] = (9, None, None)
    assert check_search_tree_order(t, "r")
    t["c"] = (7, None, None)
    assert not check_search_tree_order(t, "r")
