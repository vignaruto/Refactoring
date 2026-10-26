def tree_levels(children, root):
    levels = []
    frontier = [root]
    while frontier:
        levels.append(sorted(frontier))
        nxt = []
        for node in frontier:
            nxt.extend(children.get(node, []))
        frontier = nxt
    return levels

if __name__ == "__main__":
    kids = {"a": ["c", "b"], "b": ["d"]}
    assert tree_levels(kids, "a") == [["a"], ["b", "c"], ["d"]]
