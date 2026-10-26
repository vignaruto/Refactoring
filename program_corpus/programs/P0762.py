def det3(m):
    return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])

def trace(m):
    return sum(m[i][i] for i in range(len(m)))

def is_invertible(m, eps=1e-12):
    return abs(det3(m)) > eps

if __name__ == "__main__":
    diagonal = [[2, 0, 0], [0, 3, 0], [0, 0, 4]]
    singular = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert det3(diagonal) == 24
    assert trace(diagonal) == 9
    assert not is_invertible(singular)
