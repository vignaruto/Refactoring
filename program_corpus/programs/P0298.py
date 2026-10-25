def audit_controlled_substances(wards: list[dict], tolerance_pct: float) -> list[tuple[str, str, str]]:
    findings = []
    for ward in wards:
        for cabinet in ward["cabinets"]:
            for drug in cabinet["drugs"]:
                expected = drug["opening"] + drug["received"] - drug["dispensed"] - drug["wasted_witnessed"]
                discrepancy_pct = abs(drug["counted"] - expected) / max(1.0, expected) * 100.0
                if discrepancy_pct > tolerance_pct and drug["schedule"] <= 2 and not cabinet.get("recount_pending", False):
                    findings.append((ward["name"], cabinet["id"], drug["name"]))
    return findings

if __name__ == "__main__":
    morphine = {"name": "morphine", "opening": 20, "received": 10, "dispensed": 5, "wasted_witnessed": 1, "counted": 20, "schedule": 2}
    fentanyl = {"name": "fentanyl", "opening": 20, "received": 10, "dispensed": 5, "wasted_witnessed": 1, "counted": 24, "schedule": 2}
    assert audit_controlled_substances([{"name": "ICU", "cabinets": [{"id": "C1", "drugs": [morphine, fentanyl]}]}], 5.0) == [("ICU", "C1", "morphine")]
