from collections import deque

def even_degree_at_distance(adj, start, distance):
    depth = {start: 0}
    queue = deque([start])
    hits = []
    while queue:
        node = queue.popleft()
        for nb in adj.get(node, ()):
            if nb not in depth:
                depth[nb] = depth[node] + 1
                queue.append(nb)
        if depth[node] == distance and len(adj.get(node, ())) % 2 == 0 and node != start:
            hits.append(node)
    return sorted(hits)

if __name__ == "__main__":
    adj = {"a": ["b", "c"], "b": ["a", "d"]}
    adj["c"] = ["a"]
    adj["d"] = ["b"]
    assert even_degree_at_distance(adj, "a", 1) == ["b"]
    assert even_degree_at_distance(adj, "a", 2) == []
