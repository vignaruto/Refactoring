def can_borrow_item(member: dict, item: dict, loans: int) -> bool:
    limit = 8 if member["tier"] == "premium" else 4
    overdue = member.get("overdue_days", 0)
    if item.get("reference_only"):
        return False
    if member["active"] and overdue == 0 and loans < limit:
        return True
    elif member["active"] and overdue <= 3 and loans < 2 and item["kind"] != "dvd":
        return True
    return False

if __name__ == "__main__":
    m = {"tier": "basic", "active": True}
    assert can_borrow_item(m, {"kind": "book"}, 3)
    assert not can_borrow_item(m, {"kind": "book"}, 4)
    late = {"tier": "basic", "active": True, "overdue_days": 2}
    assert can_borrow_item(late, {"kind": "book"}, 1)
    assert not can_borrow_item(late, {"kind": "dvd"}, 1)
