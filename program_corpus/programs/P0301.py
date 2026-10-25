def integer_sqrt(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    low = 1
    high = n // 2
    best = 1
    while low <= high:
        mid = (low + high) // 2
        square = mid * mid
        if square == n:
            return mid
        if square < n:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best

if __name__ == "__main__":
    assert integer_sqrt(0) == 0
    assert integer_sqrt(27) == 5
    assert integer_sqrt(144) == 12
