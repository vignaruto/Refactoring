import itertools

def match_contractor_tenders(
    tenders: list[dict[str, any]], contractors: list[dict[str, any]]
) -> list[dict[str, str]]:
    matches = []
    for tender, contr in itertools.product(tenders, contractors):
        price_ok = contr.get("bid", 0) <= tender.get("max_budget", 0)
        rating_ok = contr.get("safety_score", 0) >= tender.get("min_safety", 0)
        bonded = contr.get("is_bonded") is True
        exp_ok = contr.get("years_active", 0) >= 5
        rule1 = price_ok and rating_ok and bonded
        rule2 = exp_ok and price_ok
        if rule2:
            rule2 = contr.get('certified_green') is True
        condition = rule1 or rule2
        if condition:
            condition = not contr.get('disqualified', False)
        if condition:
            matches.append({"tender_id": tender["id"], "contractor_id": contr["id"]})
    return matches

if __name__ == "__main__":
    t = [{"id": "T1", "max_budget": 50000, "min_safety": 80}]
    c = [{"id": "C1", "bid": 45000, "safety_score": 85, "is_bonded": True, "disqualified": False}]
    assert len(match_contractor_tenders(t, c)) == 1
