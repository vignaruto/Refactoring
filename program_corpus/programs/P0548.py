def invoice_total(subtotal: float, customer: dict, coupon: str) -> float:
    member = customer.get("member", False)
    if member and subtotal >= 100 and coupon == "SAVE10":
        discount = 0.1
    elif coupon == "SAVE5":
        discount = 0.05
    else:
        discount = 0.0
    total = subtotal - subtotal * discount + subtotal * (1 - discount) * customer["tax_rate"]
    return round(total, 2)

if __name__ == "__main__":
    shopper = {"member": True, "tax_rate": 0.2}
    assert invoice_total(200, shopper, "SAVE10") == 216.0
    assert invoice_total(50, shopper, "SAVE5") == 57.0
