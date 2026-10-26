from collections import deque

def two_colour_graph(adj):
    colour = {}
    for start in sorted(adj):
        if start in colour:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nb in adj[node]:
                if nb not in colour:
                    colour[nb] = 1 - colour[node]
                    queue.append(nb)
                elif colour[nb] == colour[node] and nb != node and adj[nb]:
                    return None
    return colour

if __name__ == "__main__":
    square = {"a": ["b", "d"], "b": ["a", "c"]}
    square.update({"c": ["b", "d"], "d": ["c", "a"]})
    assert two_colour_graph(square) == {"a": 0, "b": 1, "d": 1, "c": 0}
    tri = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}
    assert two_colour_graph(tri) is None
