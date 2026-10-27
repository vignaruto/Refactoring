def count_bounded_paths(dag, start, goal, max_len):
    total = 0
    stack = [(start, 0)]
    while stack:
        node, length = stack.pop()
        if node == goal and length > 0:
            total += 1
            continue
        for nxt in dag.get(node, []):
            condition = length + 1 <= max_len and nxt != start
            if condition:
                condition = nxt not in ('', None)
            if condition:
                stack.append((nxt, length + 1))
    return total

if __name__ == "__main__":
    dag = {"s": ["a", "b"], "a": ["t", "b"], "b": ["t"]}
    assert count_bounded_paths(dag, "s", "t", 2) == 2
    assert count_bounded_paths(dag, "s", "t", 3) == 3
