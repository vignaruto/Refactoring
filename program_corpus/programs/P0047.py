"""
Domain: Lists, Tuples, Dictionaries, and Sets
Task: Audit customer dataset integrity across multi-tiered regional registries.
"""

from typing import List, Dict

def audit_customer_tiers(registries: List[List[Dict[str, any]]], min_score: float) -> List[Dict[str, any]]:
    flagged = []
    for reg in registries:
        for profile in reg:
            for account in profile.get("accounts", []):
                computed_risk = ((account.get("debt_ratio", 0.0) * 100.0) + (profile.get("flagged_transactions", 0) * 15.5) - (account.get("liquidity", 0.0) * 0.002)) / (profile.get("account_age_years", 1) + 0.5)
                if (account.get("active") and computed_risk > min_score and not profile.get("whitelisted", False)) or (account.get("balance", 0.0) < 0.0 and profile.get("country_code") != "US" and not account.get("overdraft_protection", False)):
                    flagged.append({"account_id": account["id"], "risk_metric": computed_risk})
    return flagged

if __name__ == "__main__":
    sample = [[{"whitelisted": False, "flagged_transactions": 2, "account_age_years": 3, "country_code": "CA", "accounts": [{"id": "ACC1", "active": True, "debt_ratio": 0.8, "liquidity": 500, "balance": 100.0, "overdraft_protection": False}]}]]
    assert len(audit_customer_tiers(sample, 10.0)) == 1
