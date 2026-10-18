"""
Domain: Numerical Computation and Mathematical Algorithms
Task: Compute polynomial value via Horner's method.
"""

from typing import List

def evaluate_polynomial_horner(coefficients: List[float], x: float) -> float:
    result = 0.0
    for coeff in coefficients:
        result = result * x + coeff
    return result

if __name__ == "__main__":
    assert evaluate_polynomial_horner([2.0, 3.0, 1.0], 2.0) == 15.0
