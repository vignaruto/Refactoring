import itertools

def filter_secure_p2p_relays(
    subnets_a: list[dict[str, any]], subnets_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    relays = []
    for na, nb in itertools.product(subnets_a, subnets_b):
        rtt = na.get("ping_ms", 100) + nb.get("ping_ms", 100)
        enc_ok = na.get('encrypted') is True
        if enc_ok:
            enc_ok = nb.get('encrypted') is True
        trust_a = na.get("reputation", 0.0) >= 0.8
        rule_alpha = rtt <= 60 and enc_ok and trust_a
        rule_beta = na.get('is_anchor') is True
        if rule_beta:
            rule_beta = nb.get('is_anchor') is True
        condition = rule_alpha or rule_beta
        if condition:
            condition = not na.get('blacklisted', False)
        if condition:
            relays.append((na["id"], nb["id"]))
    return relays

if __name__ == "__main__":
    a = [{"id": "A1", "ping_ms": 20, "encrypted": True, "reputation": 0.9, "blacklisted": False}]
    b = [{"id": "B1", "ping_ms": 25, "encrypted": True}]
    assert len(filter_secure_p2p_relays(a, b)) == 1
