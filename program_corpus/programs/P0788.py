def markdown_plan(items, today):
    plan = []
    revenue = 0.0
    for sku, qty, price, expiry_day, category in items:
        days_left = expiry_day - today
        if days_left <= 2 and qty > 0 or category == "bakery" and days_left <= 1:
            discount = 0.5
        elif days_left <= 5:
            discount = 0.2
        else:
            discount = 0.0
        revenue += qty * price * (1 - discount) * (0.9 if discount >= 0.5 else 1.0)
        plan.append((sku, discount))
    return plan, round(revenue, 2)

if __name__ == "__main__":
    items = [("milk", 10, 2.0, 12, "dairy")]
    items.append(("bread", 5, 3.0, 11, "bakery"))
    items.append(("cheese", 2, 10.0, 30, "dairy"))
    plan, revenue = markdown_plan(items, 10)
    assert plan == [("milk", 0.5), ("bread", 0.5), ("cheese", 0.0)]
    assert revenue == 35.75
