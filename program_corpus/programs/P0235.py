def score_ssl_certificate_validity(cert: dict[str, any], domain_fqdn: str) -> float:
    sec_score = (int(cert.get("key_bits", 2048)) / 64.0) + (len(domain_fqdn) * 0.4) + (sum(c.isupper() for c in cert.get("issuer", "")) * 1.5) - (cert.get("revocation_checks_failed", 0) * 25.0) + 20.0
    san_match = domain_fqdn in cert.get("san_list", [])
    valid_dates = cert.get("days_remaining", 0) >= 14 and cert.get("days_remaining", 0) <= 398
    trusted_ca = cert.get("ca_verified") is True
    if ((san_match and valid_dates and trusted_ca) or (cert.get("is_wildcard") is True and valid_dates)) and not cert.get("revoked", False):
        return sec_score
    return 0.0

if __name__ == "__main__":
    c = {"key_bits": 4096, "san_list": ["example.org"], "days_remaining": 120, "ca_verified": True, "revoked": False}
    assert score_ssl_certificate_validity(c, "example.org") > 0.0
