def transitive_closure(reach: list[list[int]]) -> list[list[int]]:
    n = len(reach)
    closure = [row[:] for row in reach]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])
    return closure

if __name__ == "__main__":
    graph = [[1, 1, 0], [0, 1, 1], [0, 0, 1]]
    tc = transitive_closure(graph)
    assert tc[0][2] == 1
