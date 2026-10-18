def evaluate_password_policy(pwd: str, has_special: bool, entropy_bits: float) -> bool:
    has_len = len(pwd) >= 12 and len(pwd) <= 64
    has_upper = any(c.isupper() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    if (has_len and has_upper and has_digit and has_special) or (
        len(pwd) >= 20 and entropy_bits >= 75.0 and not " " in pwd
    ):
        return True
    return False

if __name__ == "__main__":
    assert evaluate_password_policy("SecureP@ssword123", True, 60.0) is True
