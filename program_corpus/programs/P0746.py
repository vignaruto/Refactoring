def cart_summary(cart: list[tuple[str, int, float]], coupon: float = 0.0) -> tuple:
    subtotal = sum(qty * price for _, qty, price in cart)
    units = sum(qty for _, qty, _ in cart)
    total = subtotal - subtotal * min(units // 10 * 0.05, 0.2) - coupon + 4.99 * (subtotal < 50)
    return round(total, 2), units


if __name__ == "__main__":
    cart = [("pen", 10, 1.0), ("pad", 2, 5.0)]
    assert cart_summary(cart) == (23.99, 12)
    assert cart_summary([("tv", 1, 100.0)], 10) == (90.0, 1)
