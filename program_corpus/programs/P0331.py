def wagner_whitin_min_cost(demands: list[int], setup_cost: float, holding_cost: float) -> float:
    periods = len(demands)
    dp = [float("inf")] * (periods + 1)
    dp[0] = 0.0
    for t in range(1, periods + 1):
        for s in range(1, t + 1):
            carry_cost = sum((k - s) * demands[k - 1] * holding_cost for k in range(s, t + 1))
            dp[t] = min(dp[t], dp[s - 1] + setup_cost + carry_cost)
    return round(dp[periods], 2)

if __name__ == "__main__":
    assert wagner_whitin_min_cost([20, 30, 10], 100.0, 2.0) == 200.0
