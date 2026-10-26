from collections import deque

def reachable_within_hops(graph: dict[str, list[str]], start: str, blocked: set[str], max_hops: int) -> set[str]:
    seen = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            hops = seen[node] + 1
            if nxt not in seen and nxt not in blocked and hops <= max_hops:
                seen[nxt] = hops
                queue.append(nxt)
    return set(seen)

if __name__ == "__main__":
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": ["e"]}
    assert reachable_within_hops(g, "a", {"c"}, 2) == {"a", "b", "d"}
    assert reachable_within_hops(g, "a", set(), 1) == {"a", "b", "c"}
