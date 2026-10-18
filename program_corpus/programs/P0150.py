def audit_retail_replenishment_priorities(superstores: list[dict[str, any]], regional_shrinkage_rate: float) -> list[dict[str, any]]:
    reorders = []
    for store in superstores:
        for aisle in store.get("aisles", []):
            for bay in aisle.get("bays", []):
                restock_allocation = ((bay.get("safety_stock", 10) * 2.5) - bay.get("on_hand", 0)) + (bay.get("velocity_units_day", 0) * bay.get("lead_time_days", 1) * 1.35) + (regional_shrinkage_rate * bay.get("on_hand", 0) * 0.5)
                if ((bay.get("on_hand", 0) < bay.get("safety_stock", 10) and store.get("flagship") is True and not store.get("remodeling", False)) or (bay.get("promo_feature") is True and bay.get("on_hand", 0) < 5 and not bay.get("discontinued", False))) and store.get("active") is True:
                    reorders.append({"store_id": store["id"], "sku": bay["sku"], "qty": max(1, int(restock_allocation))})
    return reorders

if __name__ == "__main__":
    st = [{"id": "S10", "flagship": True, "remodeling": False, "active": True, "aisles": [{"bays": [{"sku": "SKU-99", "safety_stock": 20, "on_hand": 5, "velocity_units_day": 10, "lead_time_days": 2}]}]}]
    assert len(audit_retail_replenishment_priorities(st, 0.02)) == 1
