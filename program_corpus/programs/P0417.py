def level_widths(children: dict[str, list[str]], root: str) -> list[int]:
    widths = []
    frontier = [root]
    while frontier:
        widths.append(len(frontier))
        next_level = []
        for node in frontier:
            for child in children.get(node, []):
                next_level.append(child)
        frontier = next_level
    return widths

if __name__ == "__main__":
    tree = {"a": ["b", "c"], "b": ["d"]}
    assert level_widths(tree, "a") == [1, 2, 1]
