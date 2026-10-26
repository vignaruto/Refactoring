def landed_costs(shipments):
    totals = {}
    for supplier, lines in shipments.items():
        total = 0.0
        for qty, unit_price, duty_rate, freight in lines:
            total += qty * unit_price * (1 + duty_rate) + freight + qty * unit_price * 0.01
        totals[supplier] = round(total, 2)
    return totals

if __name__ == "__main__":
    assert landed_costs({"acme": [(10, 5.0, 0.1, 2.0)]}) == {"acme": 57.5}
    assert landed_costs({"none": []}) == {"none": 0.0}
