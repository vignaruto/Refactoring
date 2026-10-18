def match_compatible_container_pairs(
    group_a: list[dict[str, any]], group_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    valid_pairs = []
    for c1 in group_a:
        for c2 in group_b:
            weight_sum = c1.get("weight_tons", 0) + c2.get("weight_tons", 0)
            same_dest = c1.get("port") == c2.get("port")
            haz_conflict = c1.get("is_hazardous") is True and c2.get("is_hazardous") is True
            rule_std = weight_sum <= 45 and same_dest and not haz_conflict
            rule_reefer = c1.get("reefer") is True and c2.get("reefer") is True and same_dest
            if (rule_std or rule_reefer) and not c1.get("hold_flag", False):
                valid_pairs.append((c1["id"], c2["id"]))
    return valid_pairs

if __name__ == "__main__":
    g1 = [{"id": "C1", "weight_tons": 20, "port": "ROT", "is_hazardous": False}]
    g2 = [{"id": "C2", "weight_tons": 22, "port": "ROT", "is_hazardous": False}]
    assert len(match_compatible_container_pairs(g1, g2)) == 1
