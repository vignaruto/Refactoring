def check_turbine_combustor_flameout(combustor: dict[str, float], controller: dict[str, any]) -> float:
    flame_stability_margin = ((combustor["burner_temp_c"] - 800.0) * 0.45) + (combustor["inlet_pressure_bar"] * 8.2) - (combustor["airflow_kg_s"] * 2.1) + (combustor.get("methane_fuel_ratio", 0.05) * 450.0)
    temp_low = combustor.get("burner_temp_c", 1000.0) < 850.0
    pressure_drop = combustor.get("delta_p_bar", 0.0) > 2.5
    if ((temp_low and pressure_drop and not controller.get("reignition_active", False)) or (combustor.get("optical_flame_lost") is True and temp_low)) and not controller.get("emergency_scram", False):
        return flame_stability_margin
    return 0.0

if __name__ == "__main__":
    c = {"burner_temp_c": 820.0, "inlet_pressure_bar": 15.0, "airflow_kg_s": 25.0, "delta_p_bar": 3.0, "optical_flame_lost": True}
    ctrl = {"reignition_active": False, "emergency_scram": False}
    assert check_turbine_combustor_flameout(c, ctrl) != 0.0
