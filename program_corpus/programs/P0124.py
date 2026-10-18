def evaluate_debt_tolerance(
    debt_to_income: float, credit_utilization: float, bankruptcy_flag: bool, guarantor_present: bool
) -> str:
    prime_cond = debt_to_income <= 0.35 and credit_utilization <= 0.30 and not bankruptcy_flag
    alt_cond = guarantor_present and debt_to_income <= 0.45 and credit_utilization <= 0.50
    if (prime_cond or alt_cond) and not (credit_utilization > 0.70 or bankruptcy_flag):
        return "APPROVED"
    return "DECLINED"

if __name__ == "__main__":
    res = evaluate_debt_tolerance(0.30, 0.25, False, False)
    assert res == "APPROVED"
