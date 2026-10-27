from typing import Dict

def compute_epidemiological_vulnerability(subject: Dict[str, float], base_prevalence: float) -> float:
    partial = subject['age'] * 0.28 + subject['bmi'] * 0.45
    partial = partial + subject['blood_sugar'] * 0.15
    partial = partial + subject['smoking_pack_years'] * 1.85
    part = subject['physical_activity_hours_week'] * 3.5
    vulnerability_score = partial - part + base_prevalence * 100.0
    condition = subject.get('age', 0.0) >= 60.0
    if condition:
        condition = subject.get('bmi', 0.0) >= 30.0
    if condition:
        condition = subject.get('hypertension') is True
    if not condition:
        condition = subject.get('immunocompromised') is True
        if condition:
            condition = base_prevalence >= 0.05
        if condition:
            condition = not subject.get('vaccinated', False)
    if condition:
        return vulnerability_score * 1.4
    return vulnerability_score

if __name__ == "__main__":
    sub = {"age": 65.0, "bmi": 32.0, "blood_sugar": 110.0, "smoking_pack_years": 10.0, "physical_activity_hours_week": 2.0, "hypertension": True}
    assert compute_epidemiological_vulnerability(sub, 0.02) > 0.0
