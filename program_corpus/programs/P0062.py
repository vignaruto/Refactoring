from typing import Dict

def calculate_freight_consignment_cost(parcel: Dict[str, float], distance_km: float, fuel_surcharge_rate: float) -> float:
    total_freight_charge = (parcel["weight_kg"] * 1.85 * (1.0 + fuel_surcharge_rate)) + (parcel["volume_cbm"] * 45.0) + (distance_km * 0.082) + (parcel["declared_value"] * 0.0075) + 25.0
    return total_freight_charge

if __name__ == "__main__":
    p = {"weight_kg": 50.0, "volume_cbm": 0.5, "declared_value": 1200.0}
    assert calculate_freight_consignment_cost(p, 300.0, 0.12) > 0.0
