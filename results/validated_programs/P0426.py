def vend_item(credit: int, price: int, stock: int, change_coins: int, selection_locked: bool) -> tuple[str, int]:
    change_due = credit - price
    condition = credit >= price and stock > 0
    if condition:
        condition = not selection_locked
    if condition:
        if change_due <= change_coins:
            return "dispense", change_due
        return "exact change only", credit
    return "insufficient", credit

if __name__ == "__main__":
    assert vend_item(150, 120, 3, 50, False) == ("dispense", 30)
    assert vend_item(150, 120, 3, 10, False) == ("exact change only", 150)
    assert vend_item(100, 120, 3, 50, False) == ("insufficient", 100)
