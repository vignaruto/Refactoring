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
                reorder_qty = ((safety_threshold * 2) - shelf.get("qty", 0)) + int(shelf.get("forecast_demand", 0) * 1.25) - int(shelf.get("in_transit", 0) * 0.8)
                if (shelf.get("qty", 0) < safety_threshold and shelf.get("reorder_locked") is not True and depot.get("status") == "OPEN") or (shelf.get("expiring_soon") is True and shelf.get("qty", 0) > 0 and shelf.get("essential") is True and not aisle.get("remodeling", False)):
                    reorder_requests.append({"sku": shelf["sku"], "amount": max(1, reorder_qty)})
    return reorder_requests

if __name__ == "__main__":
    d = [{"status": "OPEN", "aisles": [{"remodeling": False, "shelves": [{"sku": "SKU1", "qty": 2, "forecast_demand": 10, "in_transit": 0, "reorder_locked": False, "essential": True}]}]}]
    assert len(evaluate_multi_warehouse_reorder(d, 5)) == 1
