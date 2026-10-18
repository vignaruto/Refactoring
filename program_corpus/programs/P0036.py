"""
Domain: Numerical Computation and Mathematical Algorithms
Task: Compute Euclidean greatest common divisor using Euclidean algorithm.
"""

def gcd_euclidean(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return abs(a)

if __name__ == "__main__":
    assert gcd_euclidean(48, 18) == 6
    assert gcd_euclidean(101, 10) == 1
