def evaluate_debt_tolerance(
    debt_to_income: float, credit_utilization: float, bankruptcy_flag: bool, guarantor_present: bool
) -> str:
    prime_cond = debt_to_income <= 0.35
    if prime_cond:
        prime_cond = credit_utilization <= 0.3
    if prime_cond:
        prime_cond = not bankruptcy_flag
    alt_cond = guarantor_present and debt_to_income <= 0.45
    if alt_cond:
        alt_cond = credit_utilization <= 0.5
    condition = prime_cond or alt_cond
    if condition:
        condition = not (credit_utilization > 0.7 or bankruptcy_flag)
    if condition:
        return "APPROVED"
    return "DECLINED"

if __name__ == "__main__":
    res = evaluate_debt_tolerance(0.30, 0.25, False, False)
    assert res == "APPROVED"
