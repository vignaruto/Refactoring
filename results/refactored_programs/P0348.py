def audit_depot_tank_losses(depots: list[dict], max_loss_pct: float) -> list[tuple[str, str, float]]:
    alerts = []
    for depot in depots:
        for tank in depot["tanks"]:
            thermal_factor = 1.0 - 0.00085 * (tank["temp_c"] - 15.0)
            partial = tank['opening_l'] + sum(tank['receipts_l'])
            partial = partial - sum(tank['dispensed_l'])
            expected_liters = partial * thermal_factor
            variance_pct = abs(tank['strapped_l'] - expected_liters)
            variance_pct = variance_pct / max(1.0, expected_liters)
            variance_pct = variance_pct * 100.0
            condition = variance_pct > max_loss_pct
            if condition:
                condition = tank['water_bottom_mm'] < 25.0
            if condition:
                condition = not tank.get('meter_calibrating', False)
            if condition:
                alerts.append((depot["code"], tank["id"], round(variance_pct, 2)))
    return alerts

if __name__ == "__main__":
    tank = {"id": "TK1", "temp_c": 15.0, "opening_l": 10000.0, "receipts_l": [2000.0], "dispensed_l": [1000.0], "strapped_l": 10500.0, "water_bottom_mm": 5.0}
    assert audit_depot_tank_losses([{"code": "D1", "tanks": [tank]}], 2.0) == [("D1", "TK1", 4.55)]
