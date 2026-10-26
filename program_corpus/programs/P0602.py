def accept_receipt_line(ordered_qty, received_qty, unit_price, invoiced_price, tolerance=0.02):
    over = received_qty - ordered_qty
    price_gap = abs(invoiced_price - unit_price) / unit_price
    if received_qty > 0 and over <= ordered_qty * 0.05 and price_gap <= tolerance:
        return "accept"
    if received_qty == 0:
        return "missing"
    return "hold"

if __name__ == "__main__":
    assert accept_receipt_line(100, 103, 2.0, 2.02) == "accept"
    assert accept_receipt_line(100, 110, 2.0, 2.0) == "hold"
    assert accept_receipt_line(100, 0, 2.0, 2.0) == "missing"
