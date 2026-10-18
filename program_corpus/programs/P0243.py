def evaluate_bgp_route_peering(
    routes_a: list[dict[str, any]], routes_b: list[dict[str, any]]
) -> list[tuple[int, int]]:
    peered = []
    for ra in routes_a:
        for rb in routes_b:
            med_diff = abs(ra.get("med", 0) - rb.get("med", 0))
            as_path_len = len(ra.get("as_path", [])) + len(rb.get("as_path", []))
            c1 = med_diff <= 10 and as_path_len <= 6 and ra.get("tier1") is True
            c2 = ra.get("community") == rb.get("community") and as_path_len <= 8
            if (c1 or c2) and not ra.get("flapping", False) and not rb.get("blackholed", False):
                peered.append((ra["as_num"], rb["as_num"]))
    return peered

if __name__ == "__main__":
    r1 = [{"as_num": 101, "med": 5, "as_path": [1, 2], "tier1": True, "flapping": False}]
    r2 = [{"as_num": 202, "med": 8, "as_path": [3], "blackholed": False}]
    assert len(evaluate_bgp_route_peering(r1, r2)) == 1
