from typing import Dict

def is_network_session_authorized(
    session: Dict[str, any], client: Dict[str, any], gateway_secure: bool
) -> bool:
    is_tls = session.get("tls_version", 0.0) >= 1.3
    cert_ok = client.get("cert_valid") is True
    ip_white = client.get("whitelisted_ip") is True
    mfa_done = session.get("mfa_verified") is True
    revoked = client.get("cert_revoked") is True
    if (is_tls and cert_ok and ip_white) or (
        mfa_done and gateway_secure and not revoked
    ):
        return True
    return False

if __name__ == "__main__":
    s = {"tls_version": 1.3, "mfa_verified": False}
    c = {"cert_valid": True, "whitelisted_ip": True, "cert_revoked": False}
    assert is_network_session_authorized(s, c, True) is True
