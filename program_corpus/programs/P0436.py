def lot_release_decision(lot: dict[str, float], days_to_expiry: int, coa_received: bool) -> tuple[str, float]:
    potency_drift = abs(lot["assay"] - lot["label"]) / lot["label"] * 100.0
    sellable_fraction = max(0.0, min(1.0, days_to_expiry / 365.0)) * (1.0 - lot["damaged"])
    if potency_drift <= 5.0 and coa_received and days_to_expiry > 30:
        return "release", round(sellable_fraction, 3)
    return "quarantine", 0.0

if __name__ == "__main__":
    lot = dict(assay=98.0, label=100.0, damaged=0.1)
    assert lot_release_decision(lot, 365, True) == ("release", 0.9)
    assert lot_release_decision(lot, 10, True) == ("quarantine", 0.0)
