from math import gcd

def reduce_ratio(parts: list[int]) -> list[int]:
    if not parts or all(p == 0 for p in parts):
        return list(parts)
    common = 0
    for value in parts:
        common = gcd(common, abs(value))
    sign = -1 if all(p <= 0 for p in parts) else 1
    return [sign * p // common for p in parts]

if __name__ == "__main__":
    assert reduce_ratio([4, 6, 10]) == [2, 3, 5]
    assert reduce_ratio([-2, -4]) == [1, 2]
    assert reduce_ratio([0, 0]) == [0, 0]
