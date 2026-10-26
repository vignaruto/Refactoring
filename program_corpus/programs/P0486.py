def warranty_claim_outcome(purchase_price: float, age_months: int, warranty_months: int, physical_damage: bool, repair_quote: float) -> tuple[str, float]:
    depreciated_value = purchase_price * max(0.0, 1.0 - age_months / (warranty_months * 2.0))
    if age_months <= warranty_months and not physical_damage and repair_quote > 0.6 * depreciated_value:
        return "replace", round(depreciated_value, 2)
    if age_months <= warranty_months and not physical_damage:
        return "repair", round(repair_quote, 2)
    return "reject", 0.0

if __name__ == "__main__":
    assert warranty_claim_outcome(1000.0, 6, 12, False, 800.0) == ("replace", 750.0)
    assert warranty_claim_outcome(1000.0, 6, 12, False, 100.0) == ("repair", 100.0)
    assert warranty_claim_outcome(1000.0, 6, 12, True, 100.0) == ("reject", 0.0)
