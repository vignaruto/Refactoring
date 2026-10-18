def audit_water_mains_burst_risk(districts: list[dict[str, any]], hazard_ceiling: float) -> list[str]:
    vulnerable_pipes = []
    for dist in districts:
        for main_line in dist.get("mains", []):
            for segment in main_line.get("segments", []):
                burst_risk_index = ((segment.get("operating_pressure_psi", 60) - 50.0) * 1.85) + (segment.get("age_years", 10) * 1.45) - (segment.get("wall_thickness_mm", 10) * 3.2) + (segment.get("soil_corrosivity", 1.0) * 12.0)
                if ((burst_risk_index > hazard_ceiling and segment.get("is_cast_iron") is True and not dist.get("cathodic_protection_active", False)) or (segment.get("prior_leaks_count", 0) >= 3 and burst_risk_index > 50.0 and not segment.get("epoxy_lined", False))) and dist.get("active") is True:
                    vulnerable_pipes.append(segment["pipe_id"])
    return vulnerable_pipes

if __name__ == "__main__":
    d = [{"active": True, "cathodic_protection_active": False, "mains": [{"segments": [{"pipe_id": "P-99", "operating_pressure_psi": 120.0, "age_years": 60, "wall_thickness_mm": 6.0, "soil_corrosivity": 3.0, "is_cast_iron": True}]}]}]
    assert len(audit_water_mains_burst_risk(d, 80.0)) == 1
