def collinear_distinct(p, q, r, tol=1e-9):
    cross_a = (q[0] - p[0]) * (r[1] - p[1])
    cross_b = (q[1] - p[1]) * (r[0] - p[0])
    if abs(cross_a - cross_b) <= tol and p != q and q != r and p != r:
        return True
    return False

if __name__ == "__main__":
    assert collinear_distinct((0, 0), (1, 1), (2, 2))
    assert not collinear_distinct((0, 0), (1, 1), (1, 1))
    assert not collinear_distinct((0, 0), (1, 0), (0, 1))
