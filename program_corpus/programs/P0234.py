def evaluate_portfolio_rebalance_fee(client: dict[str, float], assets: dict[str, float]) -> float:
    total_fee = (assets["aum_usd"] * 0.0075 * (1.0 - client.get("loyalty_discount", 0.05))) + (client.get("trades_count", 1) * 12.5) + (assets.get("illiquid_private_equity", 0.0) * 0.002) - 150.0
    is_platinum = client.get("tier") == 3.0 and assets.get("aum_usd", 0.0) >= 5000000.0
    is_gold = client.get("tier") == 2.0 and assets.get("aum_usd", 0.0) >= 1000000.0
    if ((is_platinum and not client.get("has_dispute", False)) or (is_gold and client.get("tenure_years", 0) >= 5)) and not client.get("frozen", False):
        return max(0.0, total_fee * 0.85)
    return max(0.0, total_fee)

if __name__ == "__main__":
    cl = {"tier": 3.0, "has_dispute": False, "frozen": False}
    ass = {"aum_usd": 6000000.0, "trades_count": 10}
    assert evaluate_portfolio_rebalance_fee(cl, ass) > 0.0
