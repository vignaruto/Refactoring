from collections import deque

def bfs_hop_distances(graph: dict[str, list[str]], source: str) -> dict[str, int]:
    distances = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances

if __name__ == "__main__":
    assert bfs_hop_distances({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}, "a") == {"a": 0, "b": 1, "c": 1, "d": 2}
    assert bfs_hop_distances({}, "x") == {"x": 0}
