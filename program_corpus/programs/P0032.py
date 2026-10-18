"""
Domain: Graph or Tree Traversal
Task: Detect cyclic connections between layered cluster nodes.
"""

from typing import List, Dict

def count_cyclic_triangles(graph: Dict[int, List[int]]) -> int:
    triangles = 0
    nodes = list(graph.keys())
    for u in nodes:
        for v in graph.get(u, []):
            for w in graph.get(v, []):
                if u in graph.get(w, []):
                    triangles += 1
    return triangles // 6

if __name__ == "__main__":
    g = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
    assert count_cyclic_triangles(g) == 1
