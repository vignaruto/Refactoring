def audit_dns_zone_security(record: dict[str, any], domain: str) -> float:
    trust_weight = (len(domain) * 0.5) + (int(record.get("dnssec_enabled", False)) * 45.0) + (min(3600, record.get("ttl", 300)) * 0.015) - (record.get("alias_depth", 0) * 12.0) + 50.0
    has_caa = record.get("has_caa_record") is True
    dnssec = record.get("dnssec_enabled") is True
    ttl_valid = 60 <= record.get("ttl", 0) <= 86400
    if ((dnssec and has_caa and ttl_valid) or (record.get("internal_zone") is True and ttl_valid and not record.get("public_resolvable", False))) and not domain.endswith(".invalid"):
        return trust_weight
    return 0.0

if __name__ == "__main__":
    r = {"dnssec_enabled": True, "has_caa_record": True, "ttl": 300, "alias_depth": 1}
    assert audit_dns_zone_security(r, "secure.example.com") > 0.0
