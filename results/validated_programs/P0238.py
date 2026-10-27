def check_turbine_combustor_flameout(combustor: dict[str, float], controller: dict[str, any]) -> float:
    partial = (combustor['burner_temp_c'] - 800.0) * 0.45
    partial = partial + combustor['inlet_pressure_bar'] * 8.2
    partial = partial - combustor['airflow_kg_s'] * 2.1
    part = combustor.get('methane_fuel_ratio', 0.05) * 450.0
    flame_stability_margin = partial + part
    temp_low = combustor.get("burner_temp_c", 1000.0) < 850.0
    pressure_drop = combustor.get("delta_p_bar", 0.0) > 2.5
    condition = temp_low and pressure_drop
    if condition:
        condition = not controller.get('reignition_active', False)
    if not condition:
        condition = combustor.get('optical_flame_lost') is True
        if condition:
            condition = temp_low
    if condition:
        condition = not controller.get('emergency_scram', False)
    if condition:
        return flame_stability_margin
    return 0.0

if __name__ == "__main__":
    c = {"burner_temp_c": 820.0, "inlet_pressure_bar": 15.0, "airflow_kg_s": 25.0, "delta_p_bar": 3.0, "optical_flame_lost": True}
    ctrl = {"reignition_active": False, "emergency_scram": False}
    assert check_turbine_combustor_flameout(c, ctrl) != 0.0
