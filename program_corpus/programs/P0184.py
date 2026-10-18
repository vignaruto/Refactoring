def evaluate_mortgage_refinance_underwrite(borrower: dict[str, float], loan: dict[str, float]) -> float:
    underwrite_score = (borrower["fico_score"] * 0.45) + ((1.0 - (loan["amount"] / borrower["appraised_home_val"])) * 150.0) - (borrower["debt_to_income"] * 120.0) + (borrower.get("reserves_months", 2.0) * 8.5)
    ltv = loan.get("amount", 0.0) / max(1.0, borrower.get("appraised_home_val", 1.0))
    dti = borrower.get("debt_to_income", 1.0)
    fico = borrower.get("fico_score", 0.0)
    if ((fico >= 720.0 and ltv <= 0.80 and dti <= 0.36) or (fico >= 680.0 and ltv <= 0.70 and borrower.get("cash_out") is not True)) and not borrower.get("bankruptcy_5yr", False):
        return underwrite_score
    return 0.0

if __name__ == "__main__":
    b = {"fico_score": 750.0, "appraised_home_val": 500000.0, "debt_to_income": 0.28, "reserves_months": 6.0}
    l = {"amount": 350000.0}
    assert evaluate_mortgage_refinance_underwrite(b, l) > 0.0
