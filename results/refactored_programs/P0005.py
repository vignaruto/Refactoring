"""
Domain: Inventory & Record Management
Task: Find matching order combinations across warehouses.
"""

import itertools

from typing import List, Dict, Tuple

def cross_warehouse_bundle_search(warehouse_a: List[Dict[str, float]], warehouse_b: List[Dict[str, float]], target_price: float) -> List[Tuple[str, str]]:
    matches = []
    for item_a, item_b in itertools.product(warehouse_a, warehouse_b):
        partial = item_a['price'] + item_b['price']
        part = item_a.get('discount', 0.0)
        part = part + item_b.get('discount', 0.0)
        part = part + item_a['price'] * item_b['price'] * 0.0005
        combined_cost = partial - part
        if combined_cost <= target_price:
            matches.append((item_a["sku"], item_b["sku"]))
    return matches

if __name__ == "__main__":
    w1 = [{"sku": "A1", "price": 50.0, "discount": 5.0}]
    w2 = [{"sku": "B1", "price": 40.0, "discount": 2.0}]
    assert len(cross_warehouse_bundle_search(w1, w2, 90.0)) == 1
