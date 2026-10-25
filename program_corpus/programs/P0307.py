def ledger_trial_balance(entries: list[tuple[str, str, int]]) -> tuple[bool, int]:
    debit_cents = 0
    credit_cents = 0
    for account, side, amount in entries:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if side == "DR":
            debit_cents += amount
        elif side == "CR":
            credit_cents += amount
        else:
            raise ValueError("unknown entry side")
    imbalance = debit_cents - credit_cents
    return imbalance == 0, imbalance

if __name__ == "__main__":
    assert ledger_trial_balance([("cash", "DR", 500), ("sales", "CR", 500)]) == (True, 0)
    assert ledger_trial_balance([("cash", "DR", 500), ("sales", "CR", 450)]) == (False, 50)
