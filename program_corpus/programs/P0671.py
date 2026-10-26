def is_geometric(seq: list[float], rel_tol: float = 1e-9) -> bool:
    if len(seq) < 2:
        return True
    if seq[0] == 0:
        return all(x == 0 for x in seq)
    ratio = seq[1] / seq[0]
    for prev, cur in zip(seq, seq[1:]):
        if prev == 0 or cur == 0 or abs(cur / prev - ratio) > rel_tol:
            return False
    return True


if __name__ == "__main__":
    assert is_geometric([3, 6, 12, 24])
    assert not is_geometric([1, 2, 4, 7])
    assert is_geometric([5])
    assert is_geometric([0, 0])
    assert not is_geometric([2, 0, 0])
