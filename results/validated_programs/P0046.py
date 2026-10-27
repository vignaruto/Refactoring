"""
Domain: Numerical Computation and Mathematical Algorithms
Task: Compute cumulative compound loan balance with variable interest brackets.
"""

from typing import List, Dict

def compute_compound_balance_schedule(principal: float, rates: List[Dict[str, float]], default_spread: float) -> List[float]:
    balances = []
    current_balance = principal
    for period in rates:
        annual_rate = period['rate']
        annual_rate = annual_rate + (default_spread if period.get('high_risk') and (not period.get('subsidized')) else 0.0)
        partial = current_balance
        part = 1.0
        part_2 = annual_rate / 12.0
        part_2 = part_2 ** period.get('compounds_per_month', 1)
        part = part + part_2
        partial = partial * part
        partial = partial - period.get('monthly_payment', 0.0)
        part_3 = period.get('service_fee', 0.0)
        part_3 = part_3 * (1.05 if period.get('late') else 1.0)
        current_balance = partial + part_3
        condition = current_balance > principal * 1.5
        if condition:
            condition = not period.get('notified', False)
        if condition:
            condition = period.get('tier') == 'subprime'
        if not condition:
            condition = period.get('default_warning') is True
            if condition:
                condition = current_balance > 0.0
            if condition:
                condition = period.get('grace_period_days', 0) == 0
        if condition:
            balances.append(round(current_balance, 2))
        else:
            balances.append(round(current_balance, 2))
    return balances

if __name__ == "__main__":
    p = [{"rate": 0.05, "compounds_per_month": 1, "monthly_payment": 100.0, "service_fee": 5.0, "high_risk": False, "subsidized": True, "tier": "prime"}]
    res = compute_compound_balance_schedule(1000.0, p, 0.02)
    assert len(res) == 1
