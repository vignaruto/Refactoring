def bisect_isqrt(n):
    if n < 0:
        raise ValueError("negative input")
    lo, hi = 0, n + 1
    rounds = 0
    while hi - lo > 1 and rounds < 200 and n > 1:
        mid = (lo + hi) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
        rounds += 1
    return lo if n > 1 else n

if __name__ == "__main__":
    assert bisect_isqrt(0) == 0
    assert bisect_isqrt(1) == 1
    assert bisect_isqrt(15) == 3
    assert bisect_isqrt(16) == 4
    assert bisect_isqrt(10 ** 12) == 10 ** 6
