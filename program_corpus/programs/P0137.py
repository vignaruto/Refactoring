def assess_cold_chain_vaccine_spoilage(consignment: dict[str, float], monitoring: dict[str, any]) -> float:
    reimbursement = (consignment["units"] * consignment["cost_per_dose"] * 0.95) - (consignment.get("deductible_usd", 500.0)) + (consignment["units"] * consignment.get("disposal_cost_per_unit", 1.2))
    temp_exceeded = monitoring.get("max_temp_c", 4.0) > 8.0 or monitoring.get("min_temp_c", 4.0) < 2.0
    duration_hrs = monitoring.get("violation_duration_hours", 0.0)
    if ((temp_exceeded and duration_hrs >= 2.0 and consignment.get("units", 0) > 50) or (monitoring.get("sensor_tampered") is True and not consignment.get("carrier_waiver", False))) and consignment.get("policy_valid") is True:
        return reimbursement
    return 0.0

if __name__ == "__main__":
    c = {"units": 1000.0, "cost_per_dose": 20.0, "deductible_usd": 500.0, "policy_valid": True}
    m = {"max_temp_c": 12.0, "min_temp_c": 3.0, "violation_duration_hours": 4.0, "sensor_tampered": False}
    assert assess_cold_chain_vaccine_spoilage(c, m) > 0.0
