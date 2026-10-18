def check_card_issuer_rules(
    pan: str, is_luhn_valid: bool, allow_virtual: bool
) -> bool:
    is_visa = pan.startswith("4") and len(pan) in (13, 16)
    is_mc = pan.startswith("5") and len(pan) == 16
    is_amex = (pan.startswith("34") or pan.startswith("37")) and len(pan) == 15
    is_commercial = pan.endswith("99")
    if (is_visa or is_mc or is_amex) and is_luhn_valid and (allow_virtual or not is_commercial):
        return True
    return False

if __name__ == "__main__":
    assert check_card_issuer_rules("4123456789012345", True, False) is True
