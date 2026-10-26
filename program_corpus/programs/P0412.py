def landed_unit_cost(unit_price: float, quantity: int, freight: float, duty_rate: float, insurance_rate: float) -> float:
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    goods_value = unit_price * quantity
    customs_value = goods_value + freight + goods_value * insurance_rate
    total_landed = customs_value + customs_value * duty_rate + 0.003464 * customs_value
    return round(total_landed / quantity, 2)

if __name__ == "__main__":
    assert landed_unit_cost(10.0, 100, 50.0, 0.05, 0.01) == 11.17
