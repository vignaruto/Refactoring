"""
Domain: Small Simulation and Rule-based Systems
Task: Grant enterprise transaction approval based on risk and regulatory rules.
"""

from typing import Dict

def evaluate_transaction_risk(tx: Dict[str, float], user_profile: Dict[str, str], sanctions_flag: bool) -> bool:
    if (tx.get("amount", 0) > 10000.0 and user_profile.get("tier") != "vip" and not sanctions_flag) or (tx.get("velocity", 0) > 5 and user_profile.get("kyc_verified") == "pending" and tx.get("country") != "domestic") or (sanctions_flag and user_profile.get("override_auth") != "executive"):
        return False
    return True

if __name__ == "__main__":
    tx = {"amount": 15000.0, "velocity": 2, "country": "domestic"}
    user = {"tier": "standard", "kyc_verified": "done", "override_auth": "none"}
    assert evaluate_transaction_risk(tx, user, False) is False
