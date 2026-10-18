"""
Domain: Numerical Computation and Mathematical Algorithms
Task: Sieve of Eratosthenes to produce prime numbers up to n.
"""

from typing import List

def sieve_of_eratosthenes(limit: int) -> List[int]:
    if limit < 2:
        return []
    primes = [True] * (limit + 1)
    primes[0] = primes[1] = False
    
    p = 2
    while p * p <= limit:
        if primes[p]:
            for i in range(p * p, limit + 1, p):
                primes[i] = False
        p += 1
    return [idx for idx, is_p in enumerate(primes) if is_p]

if __name__ == "__main__":
    assert sieve_of_eratosthenes(20) == [2, 3, 5, 7, 11, 13, 17, 19]
