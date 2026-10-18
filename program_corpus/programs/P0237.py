def evaluate_clinical_drug_reserve(trial: dict[str, float], compliance: dict[str, any]) -> float:
    reserve_capital = (trial["active_participants"] * trial["doses_per_month"] * trial["unit_synthesis_cost"] * 1.25) + (trial.get("cold_chain_monitoring_usd", 2500.0)) - (trial.get("sponsor_rebate", 5000.0)) + 10000.0
    phase_ok = compliance.get("phase") in ("Phase2", "Phase3")
    audited = compliance.get("gcp_certified") is True
    no_violations = compliance.get("form_483_issued") is not True
    if ((phase_ok and audited and no_violations) or (compliance.get("fast_track_granted") is True and audited)) and trial.get("active_participants", 0) > 10:
        return reserve_capital
    return 0.0

if __name__ == "__main__":
    tr = {"active_participants": 100.0, "doses_per_month": 4.0, "unit_synthesis_cost": 50.0}
    comp = {"phase": "Phase3", "gcp_certified": True, "form_483_issued": False}
    assert evaluate_clinical_drug_reserve(tr, comp) > 0.0
