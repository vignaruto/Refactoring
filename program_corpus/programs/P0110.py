def evaluate_loyalty_index(history: dict[str, float], decay_rate: float, bonus_factor: float) -> float:
    tier_score = (history["spend_ytd"] * 0.12 * (1.0 + bonus_factor)) + (history["frequency_month"] * 15.5 * (1.0 - decay_rate * 0.05)) + (history["referrals_count"] * 45.0) - (history["unresolved_tickets"] * 30.0) + 100.0
    return tier_score

if __name__ == "__main__":
    rec = {"spend_ytd": 1200.0, "frequency_month": 4.0, "referrals_count": 2.0, "unresolved_tickets": 0.0}
    assert evaluate_loyalty_index(rec, 0.1, 0.05) > 0.0
