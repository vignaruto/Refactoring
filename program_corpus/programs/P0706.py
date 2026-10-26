def expand_bom(bom, product, quantity):
    needed = {}
    stack = [(product, quantity)]
    while stack:
        item, qty = stack.pop()
        parts = bom.get(item)
        if not parts:
            needed[item] = needed.get(item, 0) + qty
            continue
        for part, per_unit in parts:
            stack.append((part, qty * per_unit))
    return needed

if __name__ == "__main__":
    bom = {"bike": [("wheel", 2), ("frame", 1)]}
    bom["wheel"] = [("spoke", 32), ("rim", 1)]
    needed = expand_bom(bom, "bike", 1)
    assert needed == {"frame": 1, "rim": 2, "spoke": 64}
