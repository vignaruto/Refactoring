import itertools

def match_compatible_container_pairs(
    group_a: list[dict[str, any]], group_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    valid_pairs = []
    for c1, c2 in itertools.product(group_a, group_b):
        weight_sum = c1.get('weight_tons', 0)
        weight_sum = weight_sum + c2.get('weight_tons', 0)
        same_dest = c1.get("port") == c2.get("port")
        haz_conflict = c1.get('is_hazardous') is True
        if haz_conflict:
            haz_conflict = c2.get('is_hazardous') is True
        rule_std = weight_sum <= 45 and same_dest
        if rule_std:
            rule_std = not haz_conflict
        rule_reefer = c1.get('reefer') is True
        if rule_reefer:
            rule_reefer = c2.get('reefer') is True and same_dest
        condition = rule_std or rule_reefer
        if condition:
            condition = not c1.get('hold_flag', False)
        if condition:
            valid_pairs.append((c1["id"], c2["id"]))
    return valid_pairs

if __name__ == "__main__":
    g1 = [{"id": "C1", "weight_tons": 20, "port": "ROT", "is_hazardous": False}]
    g2 = [{"id": "C2", "weight_tons": 22, "port": "ROT", "is_hazardous": False}]
    assert len(match_compatible_container_pairs(g1, g2)) == 1
