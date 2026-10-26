def first_affordable(products, max_price, min_rating):
    for index, (name, price, rating, stock) in enumerate(products):
        if price <= max_price and rating >= min_rating and stock > 0:
            return index, name
    return -1, None

if __name__ == "__main__":
    items = [("lamp", 30, 4.5, 0), ("desk", 120, 4.8, 3)]
    items.append(("chair", 45, 4.2, 7))
    assert first_affordable(items, 50, 4.0) == (2, "chair")
    assert first_affordable(items, 20, 4.0) == (-1, None)
