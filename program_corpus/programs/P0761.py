def heating_cost(areas, u_values, inside_c, outside_c, hours, price_kwh, air_changes=0.5, volume_m3=250):
    fabric_w = sum(a * u for a, u in zip(areas, u_values)) * (inside_c - outside_c)
    ventilation_w = 0.33 * air_changes * volume_m3 * (inside_c - outside_c)
    cost = (fabric_w + ventilation_w) / 1000 * hours * price_kwh
    return round(cost, 2)

if __name__ == "__main__":
    areas, u_values = [10, 20], [2.0, 0.5]
    args = (20, 0, 10, 0.3, 0.5, 100)
    cost = heating_cost(areas, u_values, *args)
    assert cost == 2.79
