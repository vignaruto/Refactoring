from collections import deque

def reachable_sets(graph):
    reach = {}
    for start in graph:
        seen = {start}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        reach[start] = seen - {start}
    return reach

if __name__ == "__main__":
    graph = {"a": ["b"], "b": ["c"], "c": [], "d": ["a"]}
    reach = reachable_sets(graph)
    assert reach["a"] == {"b", "c"}
    assert reach["c"] == set()
    assert reach["d"] == {"a", "b", "c"}
