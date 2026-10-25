def coral_bleaching_alerts(sst_weekly: list[list[list[float]]], climatology: list[list[float]], reef_mask: list[list[bool]]) -> list[tuple[int, int, int]]:
    alerts = []
    for r, row in enumerate(sst_weekly):
        for c, weekly in enumerate(row):
            if not reef_mask[r][c]:
                continue
            maximum_monthly_mean = climatology[r][c]
            degree_heating_weeks = 0.0
            for temperature in weekly[-12:]:
                hotspot = temperature - maximum_monthly_mean
                if hotspot >= 1.0:
                    degree_heating_weeks += hotspot
            latest_hotspot = weekly[-1] - maximum_monthly_mean
            alert_level = 2 if degree_heating_weeks >= 8.0 else 1 if degree_heating_weeks >= 4.0 else 0
            if alert_level > 0 and latest_hotspot > 0.0 and (len(weekly) >= 4 or degree_heating_weeks >= 8.0):
                alerts.append((r, c, alert_level))
    return alerts

if __name__ == "__main__":
    assert coral_bleaching_alerts([[[29.5] * 4, [29.5] * 4]], [[28.0, 28.0]], [[True, False]]) == [(0, 0, 1)]
    assert coral_bleaching_alerts([[[30.5] * 4]], [[28.0]], [[True]]) == [(0, 0, 2)]
