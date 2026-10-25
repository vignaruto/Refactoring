import math

def sharpe_sortino_ratios(returns: list[float], risk_free: float) -> tuple[float, float]:
    n = len(returns)
    if n < 2:
        raise ValueError("need at least two returns")
    excess = [r - risk_free for r in returns]
    mean_excess = sum(excess) / n
    total_sd = math.sqrt(sum((e - mean_excess) ** 2 for e in excess) / (n - 1))
    downside_sd = math.sqrt(sum(min(0.0, e) ** 2 for e in excess) / n)
    sharpe = mean_excess / total_sd if total_sd > 0 else 0.0
    sortino = mean_excess / downside_sd if downside_sd > 0 else 0.0
    return round(sharpe, 4), round(sortino, 4)

if __name__ == "__main__":
    sharpe, sortino = sharpe_sortino_ratios([0.1, -0.05, 0.2, 0.0], 0.0)
    assert 0.5 < sharpe < 0.6 and sortino == 2.5
