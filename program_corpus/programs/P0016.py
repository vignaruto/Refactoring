"""
Domain: Graph or Tree Traversal
Task: Compute Depth First Search path between two nodes in a directed graph.
"""

from typing import Dict, List, Optional

def dfs_find_path(graph: Dict[str, List[str]], start: str, target: str, visited: Optional[set] = None) -> Optional[List[str]]:
    if visited is None:
        visited = set()
    visited.add(start)
    if start == target:
        return [start]
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            path = dfs_find_path(graph, neighbor, target, visited)
            if path:
                return [start] + path
    return None

if __name__ == "__main__":
    g = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
    assert dfs_find_path(g, "A", "D") == ["A", "B", "D"]
