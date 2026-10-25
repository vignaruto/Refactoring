def can_renew_loan(loan: dict[str, int], fines_due: float, item_type: str) -> tuple[bool, str]:
    limits = {"book": 3, "dvd": 1, "journal": 0}
    allowed = limits.get(item_type, 0)
    blocked = fines_due > 10.0 and loan["late"] > 0
    if loan["renewed"] >= allowed or loan["holds"] > 0 or blocked:
        return False, "denied"
    new_due = loan["due"] + (21 if item_type == "book" else 7)
    return True, f"day {new_due}"

if __name__ == "__main__":
    loan = {"renewed": 1, "holds": 0, "late": 0, "due": 10}
    assert can_renew_loan(loan, 0.0, "book") == (True, "day 31")
    assert can_renew_loan(loan, 0.0, "dvd") == (False, "denied")
    assert can_renew_loan(loan, 0.0, "journal") == (False, "denied")
