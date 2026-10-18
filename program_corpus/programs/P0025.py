"""
Domain: Data Aggregation and Statistics
Task: Calculate discounted total with category tiering and complex coupons.
"""

from typing import Dict, List

def calculate_qualified_cart_discount(cart: Dict[str, float], customer: Dict[str, any], promo_codes: List[str]) -> bool:
    if (cart.get("total_amount", 0.0) >= 150.0 and customer.get("loyalty_level") in ("gold", "platinum") and not customer.get("account_suspended", False)) or ("SUMMER50" in promo_codes and cart.get("items_count", 0) >= 3 and customer.get("registration_days", 0) > 30) or (cart.get("total_amount", 0.0) > 500.0 and not customer.get("has_chargeback", False)):
        return True
    return False

if __name__ == "__main__":
    cart_data = {"total_amount": 180.0, "items_count": 2}
    cust = {"loyalty_level": "gold", "account_suspended": False, "registration_days": 45}
    assert calculate_qualified_cart_discount(cart_data, cust, []) is True
