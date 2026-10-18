def is_rest_request_authorized(
    token: dict[str, any], payload: dict[str, any], bypass_internal: bool
) -> bool:
    is_admin = token.get("role") == "admin"
    valid_sig = token.get("signature_verified") is True
    size_ok = payload.get("bytes_len", 0) <= 1048576
    rate_ok = not token.get("throttled", False)
    rule_admin = is_admin and valid_sig and size_ok
    rule_internal = bypass_internal and valid_sig and not token.get("revoked", False)
    if (rule_admin or rule_internal) and rate_ok:
        return True
    return False

if __name__ == "__main__":
    t = {"role": "admin", "signature_verified": True, "throttled": False}
    p = {"bytes_len": 5000}
    assert is_rest_request_authorized(t, p, False) is True
