"""
Domain: Numerical Computation and Mathematical Algorithms
Task: Calculate Pearson correlation coefficient between two numeric vectors.
"""

import math
from typing import List

def pearson_correlation(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Series must be of equal size and length >= 2.")
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mean_x) ** 2 for a in x))
    den_y = math.sqrt(sum((b - mean_y) ** 2 for b in y))
    
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)

if __name__ == "__main__":
    a = [1.0, 2.0, 3.0, 4.0]
    b = [2.0, 4.0, 6.0, 8.0]
    assert round(pearson_correlation(a, b), 4) == 1.0
