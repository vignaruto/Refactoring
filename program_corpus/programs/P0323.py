def is_blood_donor_eligible(age: int, weight_kg: float, hemoglobin_g_dl: float, days_since_donation: int, recent_tattoo: bool) -> bool:
    if age < 18 or age > 65 or weight_kg < 50.0:
        return False
    if hemoglobin_g_dl < 12.5 or hemoglobin_g_dl > 18.5:
        return False
    if days_since_donation < 56 or recent_tattoo:
        return False
    return True

if __name__ == "__main__":
    assert is_blood_donor_eligible(30, 65.0, 14.2, 90, False) is True
    assert is_blood_donor_eligible(30, 65.0, 11.8, 90, False) is False
    assert is_blood_donor_eligible(30, 65.0, 14.2, 40, False) is False
