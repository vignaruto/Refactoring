def audit_grain_silos(silos: list[dict], moisture_limit: float) -> list[tuple[str, int]]:
    alerts = []
    for silo in silos:
        for depth, readings in enumerate(silo["sensor_columns"]):
            hottest = max(readings)
            spoilage_risk = 0.6 * max(0.0, silo["moisture_pct"] - moisture_limit) + 0.4 * max(0.0, hottest - silo["ambient_c"]) / 5.0
            if spoilage_risk > 1.0 and not silo["aeration_on"] and silo["fill_pct"] > 10.0:
                alerts.append((silo["id"], depth))
    return alerts

if __name__ == "__main__":
    silo = {"id": "S1", "sensor_columns": [[20.0, 22.0], [20.0, 35.0]], "moisture_pct": 15.0, "ambient_c": 20.0, "aeration_on": False, "fill_pct": 80.0}
    assert audit_grain_silos([silo], 14.0) == [("S1", 1)]
