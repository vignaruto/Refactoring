def flag_suspicious_sellers(sellers: list[dict], burst_window_hours: float) -> list[str]:
    flagged = []
    for seller in sellers:
        reviews = sorted(seller["reviews"], key=lambda r: r["hour"])
        burst_count = 0
        for i, review in enumerate(reviews):
            for later in reviews[i + 1:]:
                if later["hour"] - review["hour"] <= burst_window_hours and later["rating"] == 5 and review["rating"] == 5:
                    burst_count += 1
        unverified_share = sum(1 for r in reviews if not r["verified_purchase"]) / max(1, len(reviews))
        suspicion_score = 0.5 * min(1.0, burst_count / 10.0) + 0.3 * unverified_share + 0.2 * (1.0 if seller["account_age_days"] < 30 else 0.0)
        if suspicion_score >= 0.5 or (burst_count >= 5 and unverified_share > 0.5):
            flagged.append(seller["id"])
    return flagged

if __name__ == "__main__":
    burst = [{"hour": 0.1 * k, "rating": 5, "verified_purchase": False} for k in range(6)]
    spaced = [{"hour": 10.0 * k, "rating": 4, "verified_purchase": True} for k in range(3)]
    assert flag_suspicious_sellers([{"id": "S1", "account_age_days": 10, "reviews": burst}, {"id": "S2", "account_age_days": 400, "reviews": spaced}], 1.0) == ["S1"]
