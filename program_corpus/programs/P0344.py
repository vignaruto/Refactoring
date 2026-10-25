def allocate_blood_units(requests: list[tuple[str, str, int]], bags: list[tuple[str, str, int, int]]) -> dict[str, str]:
    used = set()
    assigned = {}
    for pid, req_abo, min_ml in requests:
        for bid, bag_abo, days_left, vol_ml in bags:
            if bid in used:
                continue
            if (bag_abo == "O" or bag_abo == req_abo) and days_left >= 2 and vol_ml >= min_ml:
                assigned[pid] = bid
                used.add(bid)
                break
    return assigned

if __name__ == "__main__":
    reqs = [("P1", "A", 450)]
    stock = [("B1", "B", 10, 500), ("B2", "O", 5, 500)]
    assert allocate_blood_units(reqs, stock) == {"P1": "B2"}
