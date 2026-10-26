def needs_purchase_order(stock: dict[str, int], supplier_active: bool, discontinued: bool) -> int:
    position = stock["have"] + stock["coming"] - stock["owed"]
    if position > stock["rop"] or not supplier_active or discontinued:
        return 0
    shortfall = stock["max"] - position
    return max(0, shortfall)

if __name__ == "__main__":
    stock = dict(have=5, coming=10, owed=3, rop=20, max=50)
    assert needs_purchase_order(stock, True, False) == 38
    assert needs_purchase_order(stock, True, True) == 0
