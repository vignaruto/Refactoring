def match_returns(receipts, returns, max_days):
    stock = {rid: list(items) for rid, items, _ in receipts}
    matched = {}
    for ret_id, sku, day in returns:
        for receipt_id, _, bought_day in receipts:
            if sku in stock[receipt_id] and 0 <= day - bought_day <= max_days and ret_id not in matched:
                matched[ret_id] = receipt_id
                stock[receipt_id].remove(sku)
    return matched

if __name__ == "__main__":
    receipts = [("r1", ["a", "b"], 1), ("r2", ["a"], 5)]
    rets = [("x1", "a", 3), ("x2", "a", 6), ("x3", "b", 40)]
    assert match_returns(receipts, rets, 30) == {"x1": "r1", "x2": "r2"}
