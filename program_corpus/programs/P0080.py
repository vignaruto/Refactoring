from typing import List

def compute_asset_covariance_table(asset_returns: List[List[float]], means: List[float]) -> List[List[float]]:
    n = len(asset_returns)
    samples = len(asset_returns[0])
    table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            table[i][j] = sum((asset_returns[i][t] - means[i]) * (asset_returns[j][t] - means[j]) for t in range(samples)) / float(samples - 1.0)
    return table

if __name__ == "__main__":
    rets = [[0.01, 0.02, 0.03], [0.02, 0.01, 0.04]]
    means = [0.02, 0.0233]
    res = compute_asset_covariance_table(rets, means)
    assert len(res) == 2
