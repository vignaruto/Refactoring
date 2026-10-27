import itertools
from typing import List, Dict

def match_candidates_to_roles(
    roles: List[Dict[str, any]],
    candidates: List[Dict[str, any]]
) -> List[Dict[str, str]]:
    matches = []
    for role, cand in itertools.product(roles, candidates):
        exp_ok = cand.get("years_exp", 0) >= role.get("min_exp", 0)
        deg_ok = cand.get("degree") == role.get("req_degree")
        loc_ok = cand.get("location") == role.get("location")
        remote = role.get("remote_ok") is True
        sal_ok = cand.get("expected_sal", 0) <= role.get("max_sal", 0)
        rule_std = exp_ok and sal_ok and (loc_ok or remote)
        rule_vet = deg_ok and exp_ok and cand.get("veteran") is True
        if rule_std or rule_vet:
            matches.append({"role_id": role["id"], "cand_id": cand["id"]})
    return matches

if __name__ == "__main__":
    r = [{"id": "R1", "min_exp": 3, "location": "NY", "remote_ok": True, "max_sal": 100000}]
    c = [{"id": "C1", "years_exp": 4, "location": "SF", "expected_sal": 90000}]
    assert len(match_candidates_to_roles(r, c)) == 1
