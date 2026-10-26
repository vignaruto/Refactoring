def match_invoices(orders, invoices, amount_tol=0.01, day_tol=5):
    matched = []
    used = set()
    for po_id, po_amount, po_day in orders:
        for inv_id, inv_amount, inv_day in invoices:
            if inv_id not in used and abs(inv_amount - po_amount) <= amount_tol * po_amount and abs(inv_day - po_day) <= day_tol:
                used.add(inv_id)
                matched.append((po_id, inv_id))
                break
    return matched, [i for i, _, _ in invoices if i not in used]

if __name__ == "__main__":
    orders = [("po1", 100.0, 1), ("po2", 50.0, 10)]
    invoices = [("i1", 50.2, 12), ("i2", 100.5, 3)]
    invoices.append(("i3", 70.0, 1))
    matched, unmatched = match_invoices(orders, invoices)
    assert matched == [("po1", "i2"), ("po2", "i1")]
    assert unmatched == ["i3"]
