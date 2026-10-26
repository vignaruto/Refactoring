def return_restock_fee(days_since_purchase: int, opened: bool, category: str, has_receipt: bool) -> float:
    if days_since_purchase > 30 or not has_receipt:
        return -1.0
    if opened and category in {"electronics", "software"} and days_since_purchase > 14:
        return 0.15
    return 0.0

if __name__ == "__main__":
    assert return_restock_fee(40, False, "toys", True) == -1.0
    assert return_restock_fee(20, True, "electronics", True) == 0.15
    assert return_restock_fee(5, True, "electronics", True) == 0.0
