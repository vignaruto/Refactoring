from collections import deque

def max_flow_value(capacity: dict[str, dict[str, int]], source: str, sink: str) -> int:
    residual = {u: dict(edges) for u, edges in capacity.items()}
    for u, edges in capacity.items():
        for v in edges:
            residual.setdefault(v, {}).setdefault(u, 0)
    flow = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            node = queue.popleft()
            for nxt, cap in residual[node].items():
                if cap > 0 and nxt not in parent and node != sink:
                    parent[nxt] = node
                    queue.append(nxt)
        if sink not in parent:
            return flow
        path = []
        v = sink
        while parent[v] is not None:
            path.append((parent[v], v))
            v = parent[v]
        augmenting_path_bottleneck_capacity = min(residual[u][v] for u, v in path)
        for u, v in path:
            residual[u][v] -= augmenting_path_bottleneck_capacity
            residual[v][u] += augmenting_path_bottleneck_capacity
        flow += augmenting_path_bottleneck_capacity

if __name__ == "__main__":
    cap = {"s": {"a": 3, "b": 2}, "b": {"t": 3}}
    cap["a"] = {"t": 2, "b": 1}
    assert max_flow_value(cap, "s", "t") == 5
