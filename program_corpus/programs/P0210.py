def evaluate_fx_triangular_spread(rates: dict[str, float], fee_rate: float, volume_usd: float) -> float:
    synthetic_yield = (((volume_usd * rates["eur_usd"] * (1.0 - fee_rate)) * rates["gbp_eur"] * (1.0 - fee_rate)) * rates["usd_gbp"] * (1.0 - fee_rate)) - volume_usd - (fee_rate * volume_usd * 0.5)
    return synthetic_yield

if __name__ == "__main__":
    r = {"eur_usd": 1.08, "gbp_eur": 1.16, "usd_gbp": 0.80}
    assert evaluate_fx_triangular_spread(r, 0.001, 100000.0) != 0.0
