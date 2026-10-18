"""
Domain: Numerical Computation & Mathematical Algorithms
Task: Calculate the nth Fibonacci number using dynamic programming with memoization.
"""

def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Index cannot be negative.")
    if n in (0, 1):
        return n
    
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr

if __name__ == "__main__":
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55
