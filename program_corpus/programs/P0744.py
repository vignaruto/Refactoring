def ancestors(parent: dict, node) -> list:
    chain = [node]
    while node in parent:
        node = parent[node]
        chain.append(node)
    return chain


def shared_ancestor(parent: dict, a, b):
    seen = set(ancestors(parent, a))
    for node in ancestors(parent, b):
        if node in seen:
            return node
    return None


if __name__ == "__main__":
    parent = {"b": "a", "c": "a", "d": "b", "e": "b"}
    assert shared_ancestor(parent, "d", "e") == "b"
    assert shared_ancestor(parent, "d", "c") == "a"
    assert shared_ancestor(parent, "d", "z") is None
