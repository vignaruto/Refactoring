def match_returns_to_invoice(returns: list[dict], invoice_lines: list[dict]) -> dict[str, str]:
    remaining = {}
    for line in invoice_lines:
        remaining[line["line_id"]] = line["qty"]
    matches = {}
    for item in returns:
        for line in invoice_lines:
            line_id = line["line_id"]
            if line["sku"] == item["sku"] and remaining[line_id] >= item["qty"] and not line.get("final_sale", False):
                remaining[line_id] -= item["qty"]
                matches[item["return_id"]] = line_id
                break
    return matches

if __name__ == "__main__":
    assert match_returns_to_invoice([{"return_id": "R1", "sku": "X", "qty": 2}, {"return_id": "R2", "sku": "Y", "qty": 1}], [{"line_id": "L1", "sku": "X", "qty": 3}, {"line_id": "L2", "sku": "Y", "qty": 1, "final_sale": True}]) == {"R1": "L1"}
