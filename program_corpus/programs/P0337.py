def release_letter_of_credit(face_usd: float, shipped_days_late: int, invoice_usd: float, clean_bill: bool, insured: bool, sanctioned: bool) -> tuple[bool, float]:
    if sanctioned or not clean_bill or not insured or shipped_days_late > 5 or invoice_usd > face_usd * 1.05:
        return False, 0.0
    overrun_usd = max(0.0, invoice_usd - face_usd)
    discrepancy_fee = (75.0 if shipped_days_late > 0 else 0.0) + 0.02 * overrun_usd + 0.0015 * invoice_usd
    net_payout = invoice_usd - discrepancy_fee
    return True, round(net_payout, 2)

if __name__ == "__main__":
    assert release_letter_of_credit(10000.0, 0, 10000.0, True, True, False) == (True, 9985.0)
    assert release_letter_of_credit(10000.0, 7, 10000.0, True, True, False) == (False, 0.0)
