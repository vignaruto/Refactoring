from typing import Optional, Dict, Any

def count_leaf_nodes(node: Optional[Dict[str, Any]]) -> int:
    if node is None:
        return 0
    left_child = node.get("left")
    right_child = node.get("right")
    if left_child is None and right_child is None:
        return 1
    result = count_leaf_nodes(left_child)
    return result + count_leaf_nodes(right_child)

if __name__ == "__main__":
    tree = {"left": {"left": None, "right": None}, "right": None}
    assert count_leaf_nodes(tree) == 1
