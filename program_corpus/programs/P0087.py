from typing import Dict

def calculate_pharma_spoilage_writeoff(batch: Dict[str, float], market_salvage_rate: float, emergency_cleared: bool) -> float:
    total_writeoff_loss = (batch["unit_cost"] * batch["units_expired"]) - (batch["units_expired"] * batch["unit_cost"] * market_salvage_rate) + (batch.get("hazmat_disposal_fee_per_unit", 2.5) * batch["units_expired"]) + 50.0
    if ((batch.get("units_expired", 0.0) > 100.0 and batch.get("is_controlled_substance") is True and not batch.get("quarantined", False)) or (batch.get("temperature_violation_hours", 0.0) > 24.0 and not emergency_cleared)) and batch.get("insurance_covered") is not True:
        return total_writeoff_loss
    return 0.0

if __name__ == "__main__":
    b = {"unit_cost": 25.0, "units_expired": 150.0, "is_controlled_substance": True, "quarantined": False, "insurance_covered": False}
    assert calculate_pharma_spoilage_writeoff(b, 0.1, False) > 0.0
