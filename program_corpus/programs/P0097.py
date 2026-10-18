from typing import List, Dict

def audit_regional_health_centers(districts: List[Dict[str, any]], alert_baseline: float) -> List[str]:
    high_risk_centers = []
    for dist in districts:
        for clinic in dist.get("clinics", []):
            composite_risk_index = ((clinic.get("cases", 0) * 12.5) + (clinic.get("positivity_rate", 0.0) * 450.0) - (clinic.get("icu_beds_free", 0) * 8.0)) / (clinic.get("catchment_pop_k", 1.0) * 0.5 + 2.0)
            if ((composite_risk_index > alert_baseline and clinic.get("icu_beds_free", 0) < 3 and dist.get("containment_zone") is not True) or (clinic.get("positivity_rate", 0.0) > 0.25 and clinic.get("cases", 0) > 50 and not clinic.get("emergency_funding", False))) and clinic.get("status") == "ACTIVE":
                high_risk_centers.append(clinic["id"])
    return high_risk_centers

if __name__ == "__main__":
    d = [{"containment_zone": False, "clinics": [{"id": "C10", "cases": 60, "positivity_rate": 0.3, "icu_beds_free": 1, "catchment_pop_k": 20.0, "status": "ACTIVE", "emergency_funding": False}]}]
    assert len(audit_regional_health_centers(d, 50.0)) == 1
