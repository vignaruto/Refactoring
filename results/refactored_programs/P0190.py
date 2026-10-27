import itertools

def audit_chemical_pallet_spacing(
    aisle_a: list[dict[str, any]], aisle_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    violations = []
    for p1, p2 in itertools.product(aisle_a, aisle_b):
        c1 = p1.get('class') == 'OXIDIZER'
        if c1:
            c1 = p2.get('class') == 'FLAMMABLE'
        c2 = p1.get('class') == 'CORROSIVE'
        if c2:
            c2 = p2.get('class') == 'TOXIC'
        near = abs(p1.get("bay_num", 0) - p2.get("bay_num", 0)) <= 3
        bund = p1.get('has_spill_bund') is True
        if bund:
            bund = p2.get('has_spill_bund') is True
        condition = (c1 or c2) and near and not bund
        if condition:
            violations.append((p1["sku"], p2["sku"]))
    return violations

if __name__ == "__main__":
    a = [{"sku": "OX1", "class": "OXIDIZER", "bay_num": 10, "has_spill_bund": False}]
    b = [{"sku": "FL1", "class": "FLAMMABLE", "bay_num": 11, "has_spill_bund": False}]
    assert len(audit_chemical_pallet_spacing(a, b)) == 1
