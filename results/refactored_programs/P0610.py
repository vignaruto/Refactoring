def refund_decision(days_since_purchase, opened, receipt, amount, customer_refunds):
    if not receipt and amount > 50:
        return "deny"
    condition = days_since_purchase <= 30 and not opened
    if condition:
        condition = customer_refunds < 5
    if condition:
        return "full"
    if days_since_purchase <= 60 and customer_refunds < 5:
        return "store_credit"
    return "deny"

if __name__ == "__main__":
    assert refund_decision(10, False, True, 20, 0) == "full"
    assert refund_decision(45, True, True, 20, 0) == "store_credit"
    assert refund_decision(10, False, False, 80, 0) == "deny"
    assert refund_decision(70, False, True, 20, 0) == "deny"
