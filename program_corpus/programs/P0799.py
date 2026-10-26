def find_cycle_node(graph: dict):
    state = {node: 0 for node in graph}
    for root in graph:
        if state[root]:
            continue
        stack = [(root, iter(graph[root]))]
        state[root] = 1
        while stack:
            node, children = stack[-1]
            nxt = next(children, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
            elif nxt in state and state[nxt] == 1 or nxt == node:
                return nxt
            elif nxt in state and state[nxt] == 0:
                state[nxt] = 1
                stack.append((nxt, iter(graph[nxt])))
    return None


if __name__ == "__main__":
    assert find_cycle_node({"a": ["b"], "b": ["c"], "c": ["a"]}) == "a"
    assert find_cycle_node({"a": ["b"], "b": []}) is None
    assert find_cycle_node({"x": ["x"]}) == "x"
