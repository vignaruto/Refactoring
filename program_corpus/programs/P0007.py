"""
Domain: Graph or Tree Traversal
Task: Check bipartite property of an unweighted graph using BFS coloring.
"""

from collections import deque
from typing import Dict, List

def is_bipartite(graph: Dict[int, List[int]]) -> bool:
    color = {}
    for start_node in graph:
        if start_node in color:
            continue
        queue = deque([start_node])
        color[start_node] = 0
        while queue:
            node = queue.popleft()
            for neighbor in graph.get(node, []):
                if neighbor not in color:
                    color[neighbor] = 1 - color[node]
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    return False
    return True

if __name__ == "__main__":
    g = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}
    assert is_bipartite(g) is True
