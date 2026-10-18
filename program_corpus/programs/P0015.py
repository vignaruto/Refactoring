"""
Domain: Data Aggregation and Statistics
Task: Calculate composite creditworthiness score via mathematical polynomial.
"""

from typing import Dict

def calculate_credit_score_index(applicant: Dict[str, float], base_rate: float, tenure_multiplier: float) -> float:
    risk_metric = ((applicant["income"] * 0.35) + (applicant["credit_history_months"] * tenure_multiplier * 12.5) - (applicant["existing_debt"] * 0.45) + (applicant["savings_balance"] * 0.15)) / (applicant["loan_amount_requested"] * base_rate + 1.0)
    return risk_metric

if __name__ == "__main__":
    app = {"income": 60000, "credit_history_months": 36, "existing_debt": 5000, "savings_balance": 15000, "loan_amount_requested": 20000}
    assert calculate_credit_score_index(app, 0.05, 1.2) > 0
