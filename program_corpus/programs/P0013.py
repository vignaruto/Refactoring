"""
Domain: Inventory and Record Management
Task: Evaluate health insurance claims eligibility under corporate policy rules.
"""

from typing import Dict

def is_claim_approved(claim: Dict[str, any], policy: Dict[str, any], member_age: int) -> bool:
    if ((claim.get("amount", 0) <= policy.get("max_coverage", 50000) and claim.get("in_network") is True) or (member_age >= 65 and claim.get("emergency") is True)) and not policy.get("lapsed", False) and (claim.get("copay_paid") is True or policy.get("waive_copay") is True):
        return True
    return False

if __name__ == "__main__":
    c = {"amount": 2000, "in_network": True, "copay_paid": True, "emergency": False}
    p = {"max_coverage": 10000, "lapsed": False, "waive_copay": False}
    assert is_claim_approved(c, p, 40) is True
