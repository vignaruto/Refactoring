def evaluate_property_appraisal(asset: dict[str, float], municipal_tax_rate: float, historic_district: bool) -> float:
    assessed_valuation = (asset["square_feet"] * asset["base_sqft_cost"] * (1.0 + asset.get("renovation_factor", 0.05))) + (asset["lot_acres"] * 45000.0) - (asset["depreciation_years"] * 1850.0) + 12000.0
    is_residential = asset.get("zone_type") == 1.0
    tenure_ok = asset.get("owner_occupied_years", 0.0) >= 5.0
    if ((assessed_valuation > 250000.0 and is_residential and tenure_ok) or (historic_district and assessed_valuation <= 500000.0 and not asset.get("commercial_use", False))) and municipal_tax_rate < 0.035:
        return assessed_valuation * 0.90
    return assessed_valuation

if __name__ == "__main__":
    p = {"square_feet": 2000.0, "base_sqft_cost": 150.0, "lot_acres": 0.5, "depreciation_years": 10.0, "zone_type": 1.0, "owner_occupied_years": 7.0}
    val = evaluate_property_appraisal(p, 0.02, False)
    assert val > 0.0
