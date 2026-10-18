from typing import Dict

def evaluate_corporate_credit_facility(firm: Dict[str, float], sector_risk: float, audit_approved: bool) -> float:
    ratio_curr = firm.get("current_assets", 0.0) / (firm.get("current_liabilities", 1.0) + 1.0)
    ebitda = firm.get("ebitda", 0.0)
    debt_service = firm.get("debt_service", 1.0)
    credit_limit = (ebitda * 3.5 * (1.0 - sector_risk * 0.4)) + (firm.get("collateral_market_value", 0.0) * 0.65) - (firm.get("existing_debt", 0.0) * 0.35)
    if (ratio_curr >= 1.5 and ebitda / debt_service >= 2.5 and sector_risk <= 0.30) or (audit_approved and firm.get("tenure_years", 0.0) >= 10.0 and not firm.get("prior_defaults", False)):
        return max(0.0, credit_limit)
    return 0.0

if __name__ == "__main__":
    f = {"current_assets": 300.0, "current_liabilities": 100.0, "ebitda": 50.0, "debt_service": 10.0, "collateral_market_value": 200.0, "existing_debt": 40.0}
    assert evaluate_corporate_credit_facility(f, 0.2, True) > 0.0
