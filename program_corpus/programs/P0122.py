def is_oauth_grant_allowed(
    req: dict[str, any], scopes: list[str], client_verified: bool
) -> bool:
    grant_type = req.get("grant_type")
    pkce_valid = req.get("pkce_verified") is True
    has_redirect = req.get("redirect_uri_match") is True
    elevated = "admin:write" in scopes
    rate_exceeded = req.get("rate_limited") is True
    rule_code = grant_type == "auth_code" and pkce_valid and has_redirect
    rule_refresh = grant_type == "refresh" and client_verified and not elevated
    if (rule_code or rule_refresh) and not rate_exceeded:
        return True
    return False

if __name__ == "__main__":
    r = {"grant_type": "auth_code", "pkce_verified": True, "redirect_uri_match": True, "rate_limited": False}
    assert is_oauth_grant_allowed(r, ["read"], True) is True
