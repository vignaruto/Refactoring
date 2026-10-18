def is_margin_trade_approved(
    account: dict[str, float], order: dict[str, any], regulator_halt: bool
) -> bool:
    equity = account.get("equity", 0.0)
    debt = account.get("margin_debt", 0.0)
    maintenance_ratio = equity / max(1.0, debt + order.get("amount", 0.0))
    tier_ok = account.get("kyc_tier", 1) >= 2
    rule_std = maintenance_ratio >= 0.30 and equity >= 25000.0 and tier_ok
    rule_sub = equity >= 100000.0 and tier_ok and not order.get("is_penny_stock", False)
    if (rule_std or rule_sub) and not regulator_halt:
        return True
    return False

if __name__ == "__main__":
    acc = {"equity": 50000.0, "margin_debt": 10000.0, "kyc_tier": 2}
    ord_info = {"amount": 5000.0, "is_penny_stock": False}
    assert is_margin_trade_approved(acc, ord_info, False) is True
