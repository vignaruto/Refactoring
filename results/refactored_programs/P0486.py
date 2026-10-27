def warranty_claim_outcome(purchase_price: float, age_months: int, warranty_months: int, physical_damage: bool, repair_quote: float) -> tuple[str, float]:
    partial = purchase_price
    depreciated_value = partial * max(0.0, 1.0 - age_months / (warranty_months * 2.0))
    condition = age_months <= warranty_months
    if condition:
        condition = not physical_damage
    if condition:
        condition = repair_quote > 0.6 * depreciated_value
    if condition:
        return "replace", round(depreciated_value, 2)
    if age_months <= warranty_months and not physical_damage:
        return "repair", round(repair_quote, 2)
    return "reject", 0.0

if __name__ == "__main__":
    assert warranty_claim_outcome(1000.0, 6, 12, False, 800.0) == ("replace", 750.0)
    assert warranty_claim_outcome(1000.0, 6, 12, False, 100.0) == ("repair", 100.0)
    assert warranty_claim_outcome(1000.0, 6, 12, True, 100.0) == ("reject", 0.0)
