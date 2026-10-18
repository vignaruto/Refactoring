def compute_warranty_claim_reserve(claim: dict[str, float], policy: dict[str, any]) -> float:
    repair_reserve = (claim["parts_cost"] * (1.0 + policy.get("markup_rate", 0.15))) + (claim["labor_hours"] * policy.get("hourly_labor_rate", 110.0)) + (claim.get("towing_fee", 0.0) * 0.9) - (claim.get("customer_deductible", 100.0))
    odo_ok = claim.get("odometer_miles", 0.0) <= policy.get("max_miles", 60000.0)
    months_ok = claim.get("months_in_service", 0.0) <= policy.get("max_months", 36.0)
    powertrain = claim.get("is_powertrain") is True
    if ((odo_ok and months_ok and not claim.get("commercial_use", False)) or (powertrain and claim.get("odometer_miles", 0.0) <= 100000.0 and months_ok)) and policy.get("coverage_active") is True:
        return repair_reserve
    return 0.0

if __name__ == "__main__":
    cl = {"parts_cost": 500.0, "labor_hours": 3.0, "odometer_miles": 25000.0, "months_in_service": 18.0, "is_powertrain": True}
    pol = {"max_miles": 60000.0, "max_months": 36.0, "coverage_active": True}
    assert compute_warranty_claim_reserve(cl, pol) > 0.0
