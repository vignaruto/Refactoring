def pick_list(order_lines, locations):
    picks = []
    for sku, qty in sorted(order_lines, key=lambda line: locations.get(line[0], "ZZ")):
        bin_code = locations.get(sku, "UNSLOTTED")
        tag = "BULK" if qty >= 50 else ""
        picks.append(f"{bin_code:<10}{sku:<8}x{qty:>3} {tag}".rstrip())
    return picks

if __name__ == "__main__":
    locations = {"nut": "A01", "bolt": "B07"}
    picks = pick_list([("bolt", 60), ("nut", 5)], locations)
    assert picks[0].split() == ["A01", "nut", "x", "5"]
    assert picks[1].split() == ["B07", "bolt", "x", "60", "BULK"]
