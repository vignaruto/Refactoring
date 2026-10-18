def evaluate_multi_port_landed_costs(vendors: list[dict[str, float]], shipments: list[dict[str, float]]) -> list[list[float]]:
    landed_costs = []
    for ven in vendors:
        row = []
        for shp in shipments:
            total_landed = (shp["declared_val"] * (1.0 + ven["tariff_rate"])) + (shp["tonnage"] * ven["freight_per_ton"]) + (shp.get("port_demurrage_days", 0) * 1250.0) + (shp["declared_val"] * ven.get("fx_hedge_pct", 0.015))
            row.append(total_landed)
        landed_costs.append(row)
    return landed_costs

if __name__ == "__main__":
    v = [{"tariff_rate": 0.05, "freight_per_ton": 85.0}]
    s = [{"declared_val": 100000.0, "tonnage": 40.0}]
    res = evaluate_multi_port_landed_costs(v, s)
    assert len(res) == 1
