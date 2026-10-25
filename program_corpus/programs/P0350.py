def flag_anomalous_lab_panels(panels: list[dict], ref_bounds: dict[str, tuple[float, float]]) -> list[str]:
    flagged = []
    for panel in panels:
        extreme_count = 0
        mahalanobis_sq = 0.0
        for analyte, value in panel["analytes"].items():
            mean, sd = ref_bounds[analyte]
            z_score = (value - mean) / max(1e-6, sd)
            mahalanobis_sq += z_score * z_score
            if abs(z_score) >= 2.5 and not panel["fasting_exempt"] and analyte != "glucose":
                extreme_count += 1
        composite_index = mahalanobis_sq / max(1, len(panel["analytes"])) + 1.5 * extreme_count - (0.8 if panel["hemolysis_index"] > 50.0 else 0.0)
        if composite_index >= 4.0 and panel["hemolysis_index"] <= 100.0 and not panel.get("retest_ordered", False):
            flagged.append(panel["sample_id"])
    return flagged

if __name__ == "__main__":
    ref = {"potassium": (4.2, 0.4), "sodium": (140.0, 2.0)}
    s1 = {"sample_id": "S1", "analytes": {"potassium": 5.6, "sodium": 147.0}, "fasting_exempt": False, "hemolysis_index": 10.0}
    s2 = {"sample_id": "S2", "analytes": {"potassium": 4.3, "sodium": 140.5}, "fasting_exempt": False, "hemolysis_index": 10.0}
    assert flag_anomalous_lab_panels([s1, s2], ref) == ["S1"]
