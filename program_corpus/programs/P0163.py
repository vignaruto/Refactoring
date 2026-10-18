def compute_drug_holding_depreciation(inventory_val: float, storage_temp_c: float, humidity_pct: float, remaining_shelf_life_days: float) -> float:
    loss_amount = (inventory_val * 0.0012 * max(0.0, storage_temp_c - 4.0)) + (inventory_val * 0.0008 * max(0.0, humidity_pct - 60.0)) + (inventory_val / max(1.0, remaining_shelf_life_days) * 0.45) + 15.0
    return loss_amount

if __name__ == "__main__":
    val = compute_drug_holding_depreciation(50000.0, 8.0, 65.0, 90.0)
    assert val > 0.0
