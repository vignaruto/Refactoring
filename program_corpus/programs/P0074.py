from typing import Dict

def is_candidate_eligible(patient: Dict[str, float], consent_signed: bool) -> bool:
    age = patient.get("age", 0.0)
    bmi = patient.get("bmi", 0.0)
    bp = patient.get("systolic_bp", 0.0)
    hba1c = patient.get("hba1c", 0.0)
    cond_a = age >= 18.0 and age <= 65.0 and bmi < 32.0 and bp < 140.0
    cond_b = age > 65.0 and hba1c < 6.5 and bp < 130.0
    if (cond_a or cond_b) and consent_signed and not patient.get("pregnant", False):
        return True
    return False

if __name__ == "__main__":
    pat = {"age": 45.0, "bmi": 26.0, "systolic_bp": 125.0, "pregnant": False}
    assert is_candidate_eligible(pat, True) is True
