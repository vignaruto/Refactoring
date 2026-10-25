def trace_root_ancestors(parents: dict[str, str], node: str) -> list[str]:
    chain = []
    seen = set()
    current = node
    while current is not None:
        if current in seen:
            raise ValueError("cycle detected in parent links")
        seen.add(current)
        chain.append(current)
        current = parents.get(current)
    return chain

if __name__ == "__main__":
    assert trace_root_ancestors({"d": "b", "b": "a"}, "d") == ["d", "b", "a"]
    assert trace_root_ancestors({}, "root") == ["root"]
