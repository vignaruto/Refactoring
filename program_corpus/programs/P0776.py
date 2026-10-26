def approve_write_off(qty, unit_cost, reason, approver_level):
    value = qty * unit_cost
    if reason in ("damaged", "expired") and value <= 500 and approver_level >= 1:
        return "approved"
    if value > 500 and approver_level >= 2 or reason == "audit":
        return "approved"
    return "escalate"

if __name__ == "__main__":
    assert approve_write_off(10, 20, "damaged", 1) == "approved"
    assert approve_write_off(100, 20, "damaged", 1) == "escalate"
    assert approve_write_off(100, 20, "lost", 2) == "approved"
    assert approve_write_off(1, 1, "audit", 0) == "approved"
