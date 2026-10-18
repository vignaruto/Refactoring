from typing import Dict

def can_auto_approve_refund(
    order: Dict[str, any], item: Dict[str, any], days_since_delivery: int
) -> bool:
    is_prime = order.get("member_tier") == "prime"
    cost = item.get("unit_price", 0.0)
    unopened = item.get("sealed_box") is True
    has_dispute = order.get("open_disputes", 0) > 0
    fraud_score = order.get("fraud_score", 0.0)
    rule1 = days_since_delivery <= 30 and unopened and cost <= 250.0
    rule2 = is_prime and days_since_delivery <= 45 and cost <= 100.0
    if (rule1 or rule2) and not has_dispute and fraud_score < 0.15:
        return True
    return False

if __name__ == "__main__":
    o = {"member_tier": "prime", "open_disputes": 0, "fraud_score": 0.05}
    it = {"unit_price": 80.0, "sealed_box": False}
    assert can_auto_approve_refund(o, it, 20) is True
