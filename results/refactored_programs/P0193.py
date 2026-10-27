import itertools

def audit_mesh_service_links(
    services_a: list[dict[str, any]], services_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    allowed = []
    for sa, sb in itertools.product(services_a, services_b):
        mtls = sa.get('mtls_strict') is True
        if mtls:
            mtls = sb.get('mtls_strict') is True
        ns_match = sa.get("namespace") == sb.get("namespace")
        c1 = mtls and ns_match and sa.get("egress_open") is True
        c2 = sa.get('is_gateway') is True and mtls
        if c2:
            c2 = sb.get('public_facing') is not True
        condition = (c1 or c2) and not sa.get('isolated', False)
        if condition:
            allowed.append((sa["name"], sb["name"]))
    return allowed

if __name__ == "__main__":
    s1 = [{"name": "auth", "mtls_strict": True, "namespace": "prod", "egress_open": True}]
    s2 = [{"name": "db", "mtls_strict": True, "namespace": "prod"}]
    assert len(audit_mesh_service_links(s1, s2)) == 1
