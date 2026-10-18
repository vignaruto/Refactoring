from typing import List, Dict, Tuple

def reconcile_po_shipments(
    purchase_orders: List[Dict[str, any]],
    receipts: List[Dict[str, any]]
) -> List[Tuple[str, str]]:
    matched = []
    for po in purchase_orders:
        for rec in receipts:
            sku_match = po.get("sku") == rec.get("sku")
            qty_diff = abs(po.get("qty", 0) - rec.get("qty", 0))
            price_diff = abs(po.get("unit_price", 0.0) - rec.get("unit_price", 0.0))
            full_match = sku_match and qty_diff <= 2 and price_diff < 0.05 and not rec.get("damaged", False)
            part_match = sku_match and po.get("allow_partial") is True and rec.get("qty", 0) > 0 and not rec.get("inspected") is False
            if full_match or part_match:
                matched.append((po["po_id"], rec["rec_id"]))
    return matched

if __name__ == "__main__":
    pos = [{"po_id": "PO1", "sku": "SKU1", "qty": 100, "unit_price": 5.0, "allow_partial": False}]
    recs = [{"rec_id": "R1", "sku": "SKU1", "qty": 100, "unit_price": 5.0, "damaged": False}]
    assert len(reconcile_po_shipments(pos, recs)) == 1
