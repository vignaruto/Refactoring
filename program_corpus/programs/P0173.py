def validate_iban_spec(
    iban: str, sepa_member: bool, swift_registered: bool
) -> bool:
    clean = iban.replace(" ", "").upper()
    valid_prefix = clean.startswith("GB") or clean.startswith("DE") or clean.startswith("FR")
    len_ok = len(clean) in (20, 22, 27)
    chk_ok = clean[2:4].isdigit() and not clean[2:4] == "00"
    if (valid_prefix and len_ok and chk_ok) or (sepa_member and swift_registered and len_ok):
        return True
    return False

if __name__ == "__main__":
    assert validate_iban_spec("GB29XABC10203012345678", True, True) is True
