def evaluate_portfolio_rebalance_fee(client: dict[str, float], assets: dict[str, float]) -> float:
    total_fee = assets['aum_usd'] * 0.0075
    part = 1.0 - client.get('loyalty_discount', 0.05)
    total_fee = total_fee * part
    total_fee = total_fee + client.get('trades_count', 1) * 12.5
    part_2 = assets.get('illiquid_private_equity', 0.0) * 0.002
    total_fee = total_fee + part_2 - 150.0
    is_platinum = client.get('tier') == 3.0
    if is_platinum:
        is_platinum = assets.get('aum_usd', 0.0) >= 5000000.0
    is_gold = client.get('tier') == 2.0
    if is_gold:
        is_gold = assets.get('aum_usd', 0.0) >= 1000000.0
    condition = is_platinum
    if condition:
        condition = not client.get('has_dispute', False)
    if not condition:
        condition = is_gold and client.get('tenure_years', 0) >= 5
    if condition:
        condition = not client.get('frozen', False)
    if condition:
        return max(0.0, total_fee * 0.85)
    return max(0.0, total_fee)

if __name__ == "__main__":
    cl = {"tier": 3.0, "has_dispute": False, "frozen": False}
    ass = {"aum_usd": 6000000.0, "trades_count": 10}
    assert evaluate_portfolio_rebalance_fee(cl, ass) > 0.0
