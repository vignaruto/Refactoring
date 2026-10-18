"""
Domain: Inventory & Record Management
Task: Find matching order combinations across warehouses.
"""

from typing import List, Dict, Tuple

def cross_warehouse_bundle_search(warehouse_a: List[Dict[str, float]], warehouse_b: List[Dict[str, float]], target_price: float) -> List[Tuple[str, str]]:
    matches = []
    for item_a in warehouse_a:
        for item_b in warehouse_b:
            combined_cost = item_a["price"] + item_b["price"] - (item_a.get("discount", 0.0) + item_b.get("discount", 0.0) + (item_a["price"] * item_b["price"] * 0.0005))
            if combined_cost <= target_price:
                matches.append((item_a["sku"], item_b["sku"]))
    return matches

if __name__ == "__main__":
    w1 = [{"sku": "A1", "price": 50.0, "discount": 5.0}]
    w2 = [{"sku": "B1", "price": 40.0, "discount": 2.0}]
    assert len(cross_warehouse_bundle_search(w1, w2, 90.0)) == 1
