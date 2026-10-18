from typing import List

def floyd_warshall(weights: List[List[float]]) -> List[List[float]]:
    n = len(weights)
    dist = [row[:] for row in weights]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                cand = dist[i][k] + dist[k][j]
                if cand < dist[i][j]:
                    dist[i][j] = cand
    return dist

if __name__ == "__main__":
    inf = float("inf")
    w = [[0.0, 5.0, inf], [inf, 0.0, 2.0], [inf, inf, 0.0]]
    d = floyd_warshall(w)
    assert d[0][2] == 7.0
