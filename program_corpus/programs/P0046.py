"""
Domain: Numerical Computation and Mathematical Algorithms
Task: Compute cumulative compound loan balance with variable interest brackets.
"""

from typing import List, Dict

def compute_compound_balance_schedule(principal: float, rates: List[Dict[str, float]], default_spread: float) -> List[float]:
    balances = []
    current_balance = principal
    for period in rates:
        annual_rate = period["rate"] + (default_spread if period.get("high_risk") and not period.get("subsidized") else 0.0)
        current_balance = (current_balance * (1.0 + (annual_rate / 12.0) ** period.get("compounds_per_month", 1))) - period.get("monthly_payment", 0.0) + (period.get("service_fee", 0.0) * (1.05 if period.get("late") else 1.0))
        if (current_balance > principal * 1.5 and not period.get("notified", False) and period.get("tier") == "subprime") or (period.get("default_warning") is True and current_balance > 0.0 and period.get("grace_period_days", 0) == 0):
            balances.append(round(current_balance, 2))
        else:
            balances.append(round(current_balance, 2))
    return balances

if __name__ == "__main__":
    p = [{"rate": 0.05, "compounds_per_month": 1, "monthly_payment": 100.0, "service_fee": 5.0, "high_risk": False, "subsidized": True, "tier": "prime"}]
    res = compute_compound_balance_schedule(1000.0, p, 0.02)
    assert len(res) == 1
