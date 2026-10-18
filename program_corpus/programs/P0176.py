def is_flight_crew_duty_legal(
    pilot: dict[str, float], flight_plan: dict[str, any], augmented_crew: bool
) -> bool:
    duty_hrs = pilot.get("duty_hours_today", 0.0)
    rest_hrs = pilot.get("rest_hours_prior", 12.0)
    sectors = flight_plan.get("sectors_count", 1)
    night = flight_plan.get("is_night_flight") is True
    cond_std = duty_hrs <= 12.0 and rest_hrs >= 10.0 and sectors <= 4
    cond_aug = augmented_crew and duty_hrs <= 16.0 and rest_hrs >= 14.0
    if (cond_std or cond_aug) and not (night and duty_hrs > 10.0 and not augmented_crew):
        return True
    return False

if __name__ == "__main__":
    p = {"duty_hours_today": 8.0, "rest_hours_prior": 12.0}
    fp = {"sectors_count": 2, "is_night_flight": False}
    assert is_flight_crew_duty_legal(p, fp, False) is True
