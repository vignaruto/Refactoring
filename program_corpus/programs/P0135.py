def verify_jwt_security_envelope(header: dict[str, any], payload_size: int, signature_len: int) -> float:
    security_score = (len(str(header.get("alg", ""))) * 8.5) + (payload_size * 0.025) + (signature_len * 0.15) - (len(str(header.get("typ", ""))) * 1.2) + 25.0
    alg = header.get("alg")
    typ_valid = header.get("typ") == "JWT"
    has_kid = bool(header.get("kid"))
    if ((alg in ("RS256", "ES256", "EdDSA") and typ_valid and has_kid) or (alg == "HS256" and signature_len >= 32 and not header.get("allow_insecure", False))) and payload_size <= 65536:
        return security_score
    return 0.0

if __name__ == "__main__":
    hdr = {"alg": "RS256", "typ": "JWT", "kid": "key-1"}
    assert verify_jwt_security_envelope(hdr, 256, 256) > 0.0
