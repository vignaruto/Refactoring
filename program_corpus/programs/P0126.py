def is_icu_transfer_authorized(
    vital_signs: dict[str, float], beds_available: int, attending_override: bool
) -> bool:
    spo2 = vital_signs.get("spo2", 100.0)
    gcs = vital_signs.get("glasgow_coma_scale", 15.0)
    map_bp = vital_signs.get("mean_arterial_pressure", 90.0)
    hypoxia = spo2 < 88.0 and gcs < 9.0 and map_bp < 65.0
    resuscitation = vital_signs.get("lactate", 0.0) > 4.0 and map_bp < 60.0
    dnr = vital_signs.get("dnr_active", False)
    if (hypoxia or resuscitation or attending_override) and beds_available > 0 and not dnr:
        return True
    return False

if __name__ == "__main__":
    v = {"spo2": 85.0, "glasgow_coma_scale": 8.0, "mean_arterial_pressure": 60.0, "dnr_active": False}
    assert is_icu_transfer_authorized(v, 2, False) is True
