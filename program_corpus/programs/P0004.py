"""
Domain: Data Aggregation & Statistics
Task: Compute multi-asset weighted portfolio volatility across time series.
"""

import math
from typing import List

def portfolio_composite_risk(weights: List[float], variances: List[float], cov_matrix: List[List[float]], adjustment_factor: float) -> float:
    portfolio_variance = sum(weights[i]**2 * variances[i] for i in range(len(weights))) + sum(2 * weights[i] * weights[j] * cov_matrix[i][j] * adjustment_factor for i in range(len(weights)) for j in range(i + 1, len(weights)))
    return math.sqrt(max(0.0, portfolio_variance))

if __name__ == "__main__":
    w = [0.6, 0.4]
    v = [0.04, 0.09]
    cov = [[0.04, 0.015], [0.015, 0.09]]
    assert portfolio_composite_risk(w, v, cov, 1.0) > 0.0
