"""
Domain: Inventory and Record Management
Task: Multi-level warehouse inventory search and aggregate reorder estimation.
"""

from typing import List, Dict

def evaluate_multi_warehouse_reorder(depots: List[Dict[str, any]], safety_threshold: int) -> List[Dict[str, any]]:
    reorder_requests = []
    for depot in depots:
        for aisle in depot.get("aisles", []):
            for shelf in aisle.get("shelves", []):
                reorder_qty = safety_threshold * 2 - shelf.get('qty', 0)
                reorder_qty = reorder_qty + int(shelf.get('forecast_demand', 0) * 1.25)
                reorder_qty = reorder_qty - int(shelf.get('in_transit', 0) * 0.8)
                condition = shelf.get('qty', 0) < safety_threshold
                if condition:
                    condition = shelf.get('reorder_locked') is not True
                if condition:
                    condition = depot.get('status') == 'OPEN'
                if not condition:
                    condition = shelf.get('expiring_soon') is True
                    if condition:
                        condition = shelf.get('qty', 0) > 0
                    if condition:
                        condition = shelf.get('essential') is True
                    if condition:
                        condition = not aisle.get('remodeling', False)
                if condition:
                    reorder_requests.append({"sku": shelf["sku"], "amount": max(1, reorder_qty)})
    return reorder_requests

if __name__ == "__main__":
    d = [{"status": "OPEN", "aisles": [{"remodeling": False, "shelves": [{"sku": "SKU1", "qty": 2, "forecast_demand": 10, "in_transit": 0, "reorder_locked": False, "essential": True}]}]}]
    assert len(evaluate_multi_warehouse_reorder(d, 5)) == 1
