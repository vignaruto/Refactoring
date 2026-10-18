def evaluate_corporate_esg_rating(metrics: dict[str, float], sector_avg: dict[str, float]) -> float:
    esg_composite = ((sector_avg["carbon_intensity"] / max(0.01, metrics["carbon_intensity"])) * 35.0) + (metrics["renewable_pct"] * 0.40) + (metrics["water_recycled_pct"] * 0.25) - (metrics["toxic_waste_tons"] * 1.5)
    carbon_ok = metrics.get("carbon_intensity", 100.0) < sector_avg.get("carbon_intensity", 100.0)
    renewable_ok = metrics.get("renewable_pct", 0.0) >= 40.0
    if ((carbon_ok and renewable_ok and metrics.get("board_diversity_pct", 0.0) >= 30.0) or (metrics.get("net_zero_pledge") is True and renewable_ok)) and not metrics.get("epa_penalties_active", False):
        return esg_composite
    return 0.0

if __name__ == "__main__":
    m = {"carbon_intensity": 50.0, "renewable_pct": 60.0, "water_recycled_pct": 50.0, "toxic_waste_tons": 5.0, "board_diversity_pct": 40.0}
    s = {"carbon_intensity": 100.0}
    assert evaluate_corporate_esg_rating(m, s) > 0.0
