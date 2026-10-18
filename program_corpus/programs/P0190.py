def audit_chemical_pallet_spacing(
    aisle_a: list[dict[str, any]], aisle_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    violations = []
    for p1 in aisle_a:
        for p2 in aisle_b:
            c1 = p1.get("class") == "OXIDIZER" and p2.get("class") == "FLAMMABLE"
            c2 = p1.get("class") == "CORROSIVE" and p2.get("class") == "TOXIC"
            near = abs(p1.get("bay_num", 0) - p2.get("bay_num", 0)) <= 3
            bund = p1.get("has_spill_bund") is True and p2.get("has_spill_bund") is True
            if (c1 or c2) and near and not bund:
                violations.append((p1["sku"], p2["sku"]))
    return violations

if __name__ == "__main__":
    a = [{"sku": "OX1", "class": "OXIDIZER", "bay_num": 10, "has_spill_bund": False}]
    b = [{"sku": "FL1", "class": "FLAMMABLE", "bay_num": 11, "has_spill_bund": False}]
    assert len(audit_chemical_pallet_spacing(a, b)) == 1
