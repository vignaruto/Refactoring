def is_firewall_packet_permitted(
    pkt: dict[str, any], trusted_zone: bool, inspect_deep: bool
) -> bool:
    syn_ack = pkt.get("flags") == "SYN_ACK"
    port_ok = pkt.get("dest_port") in (80, 443, 8080)
    geo_blocked = pkt.get("country_blocked") is True
    has_sig = pkt.get("malware_signature_match") is True
    rule1 = syn_ack and port_ok and trusted_zone
    rule2 = inspect_deep and not has_sig and not geo_blocked
    if (rule1 or rule2) and not (geo_blocked and not trusted_zone):
        return True
    return False

if __name__ == "__main__":
    p = {"flags": "SYN_ACK", "dest_port": 443, "country_blocked": False, "malware_signature_match": False}
    assert is_firewall_packet_permitted(p, True, True) is True
