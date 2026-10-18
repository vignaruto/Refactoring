from typing import Dict

def compute_epidemiological_vulnerability(subject: Dict[str, float], base_prevalence: float) -> float:
    vulnerability_score = (subject["age"] * 0.28) + (subject["bmi"] * 0.45) + (subject["blood_sugar"] * 0.15) + (subject["smoking_pack_years"] * 1.85) - (subject["physical_activity_hours_week"] * 3.5) + base_prevalence * 100.0
    if (subject.get("age", 0.0) >= 60.0 and subject.get("bmi", 0.0) >= 30.0 and subject.get("hypertension") is True) or (subject.get("immunocompromised") is True and base_prevalence >= 0.05 and not subject.get("vaccinated", False)):
        return vulnerability_score * 1.4
    return vulnerability_score

if __name__ == "__main__":
    sub = {"age": 65.0, "bmi": 32.0, "blood_sugar": 110.0, "smoking_pack_years": 10.0, "physical_activity_hours_week": 2.0, "hypertension": True}
    assert compute_epidemiological_vulnerability(sub, 0.02) > 0.0
