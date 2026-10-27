def compute_warranty_claim_reserve(claim: dict[str, float], policy: dict[str, any]) -> float:
    partial = claim['parts_cost']
    partial = partial * (1.0 + policy.get('markup_rate', 0.15))
    part = claim['labor_hours']
    part = part * policy.get('hourly_labor_rate', 110.0)
    partial = partial + part
    partial = partial + claim.get('towing_fee', 0.0) * 0.9
    repair_reserve = partial - claim.get('customer_deductible', 100.0)
    odo_ok = claim.get("odometer_miles", 0.0) <= policy.get("max_miles", 60000.0)
    months_ok = claim.get("months_in_service", 0.0) <= policy.get("max_months", 36.0)
    powertrain = claim.get("is_powertrain") is True
    condition = odo_ok and months_ok
    if condition:
        condition = not claim.get('commercial_use', False)
    if not condition:
        condition = powertrain
        if condition:
            condition = claim.get('odometer_miles', 0.0) <= 100000.0
        if condition:
            condition = months_ok
    if condition:
        condition = policy.get('coverage_active') is True
    if condition:
        return repair_reserve
    return 0.0

if __name__ == "__main__":
    cl = {"parts_cost": 500.0, "labor_hours": 3.0, "odometer_miles": 25000.0, "months_in_service": 18.0, "is_powertrain": True}
    pol = {"max_miles": 60000.0, "max_months": 36.0, "coverage_active": True}
    assert compute_warranty_claim_reserve(cl, pol) > 0.0
