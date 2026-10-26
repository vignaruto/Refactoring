def adjacency_with_degrees(n, edges):
    matrix = [[0] * n for _ in range(n)]
    for u, v in edges:
        matrix[u][v] = 1
        matrix[v][u] = 1
    degrees = []
    for row in matrix:
        total = 0
        for cell in row:
            total += cell
        degrees.append(total)
    return matrix, degrees

if __name__ == "__main__":
    edges = [(0, 1), (1, 2)]
    matrix, degrees = adjacency_with_degrees(3, edges)
    assert degrees == [1, 2, 1]
    assert matrix[0] == [0, 1, 0]
