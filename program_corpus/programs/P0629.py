from math import gcd

def primitive_two_square_sums(limit):
    results = []
    for n in range(1, limit + 1):
        a = 1
        while a * a * 2 <= n:
            b_sq = n - a * a
            b = int(b_sq ** 0.5)
            if b * b == b_sq and a <= b and gcd(a, b) == 1:
                results.append((n, a, b))
            a += 1
    return results

if __name__ == "__main__":
    assert primitive_two_square_sums(10) == [(2, 1, 1), (5, 1, 2), (10, 1, 3)]
