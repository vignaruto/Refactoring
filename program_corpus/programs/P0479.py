def explode_bill_of_materials(bom: dict[str, list[tuple[str, int]]], product: str, quantity: int) -> dict[str, int]:
    totals: dict[str, int] = {}
    frontier = [(product, quantity)]
    while frontier:
        item, qty = frontier.pop()
        for component, per_unit in bom.get(item, []):
            totals[component] = totals.get(component, 0) + qty * per_unit
            frontier.append((component, qty * per_unit))
    return totals

if __name__ == "__main__":
    bom = {"bike": [("wheel", 2), ("frame", 1)]}
    bom["wheel"] = [("spoke", 32)]
    expected = {"wheel": 6, "frame": 3, "spoke": 192}
    assert explode_bill_of_materials(bom, "bike", 3) == expected
