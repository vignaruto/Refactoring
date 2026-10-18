def is_cardiac_emergency_triggered(
    vitals: dict[str, float], pacemaker_active: bool, false_alarm_history: int
) -> bool:
    hr = vitals.get("heart_rate_bpm", 75.0)
    qt = vitals.get("qt_interval_ms", 400.0)
    st = vitals.get("st_elevation_mm", 0.0)
    arrhythmia = (hr < 40.0 or hr > 160.0) and qt > 480.0
    infarction = st >= 2.0 and vitals.get("troponin_ug_l", 0.0) > 0.04
    if (arrhythmia or infarction) and not (pacemaker_active and hr > 60.0) and false_alarm_history < 3:
        return True
    return False

if __name__ == "__main__":
    v = {"heart_rate_bpm": 170.0, "qt_interval_ms": 500.0, "st_elevation_mm": 2.5, "troponin_ug_l": 0.08}
    assert is_cardiac_emergency_triggered(v, False, 1) is True
