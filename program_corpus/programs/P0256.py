def degree_counts(edges: list[tuple[str, str]]) -> dict[str, tuple[int, int]]:
    ins: dict[str, int] = {}
    outs: dict[str, int] = {}
    for source, target in edges:
        outs[source] = outs.get(source, 0) + 1
        ins[target] = ins.get(target, 0) + 1
    degrees = {}
    for node in sorted(set(ins) | set(outs)):
        degrees[node] = (ins.get(node, 0), outs.get(node, 0))
    return degrees

if __name__ == "__main__":
    assert degree_counts([("a", "b"), ("a", "c"), ("c", "a")]) == {"a": (1, 2), "b": (1, 0), "c": (1, 1)}
    assert degree_counts([]) == {}
