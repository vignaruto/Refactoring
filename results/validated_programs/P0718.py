def level_scores(children, weights, root, bonus=0.5):
    totals = []
    level = [root]
    depth = 0
    while level:
        level_total = 0.0
        nxt = []
        for node in level:
            score = weights.get(node, 0) * (depth + 1)
            score = score + bonus * len(children.get(node, []))
            level_total += score
            nxt.extend(children.get(node, []))
        totals.append(level_total)
        level = nxt
        depth += 1
    return totals

if __name__ == "__main__":
    children = {"r": ["a", "b"], "a": ["c"]}
    weights = {"r": 1, "a": 2, "b": 3, "c": 4}
    assert level_scores(children, weights, "r") == [2.0, 10.5, 12.0]
