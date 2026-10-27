def is_duty_drawback_eligible(
    claim: dict[str, any], days_since_export: int, customs_verified: bool
) -> bool:
    val = claim.get("claimed_refund_usd", 0.0)
    re_export = claim.get("re_exported_unchanged") is True
    has_cert = claim.get("certificate_of_origin") is True
    valid_window = days_since_export <= 1095 and val <= 250000.0
    condition = re_export and has_cert and valid_window
    if not condition:
        condition = customs_verified and valid_window
    if condition:
        condition = val > 0.0
    if condition:
        return True
    return False

if __name__ == "__main__":
    cl = {"claimed_refund_usd": 15000.0, "re_exported_unchanged": True, "certificate_of_origin": True}
    assert is_duty_drawback_eligible(cl, 180, True) is True
