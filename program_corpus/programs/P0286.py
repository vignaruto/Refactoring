def hvac_compressor_stages(outdoor_c: float, indoor_c: float, setpoint_c: float, occupants: int, floor_area_m2: float, solar_gain_w: float, max_stages: int) -> int:
    cooling_load_w = 3.2 * floor_area_m2 * max(0.0, outdoor_c - setpoint_c) + 75.0 * occupants + 0.6 * solar_gain_w + 12.0 * floor_area_m2
    if indoor_c <= setpoint_c - 0.5 or (outdoor_c < 12.0 and indoor_c < setpoint_c + 2.0) or max_stages <= 0:
        return 0
    stage_capacity_w = 3500.0
    stages = int(-(-cooling_load_w // stage_capacity_w))
    return min(max_stages, max(1, stages))

if __name__ == "__main__":
    assert hvac_compressor_stages(32.0, 26.0, 24.0, 10, 100.0, 2000.0, 4) == 2
    assert hvac_compressor_stages(10.0, 24.5, 24.0, 10, 100.0, 2000.0, 4) == 0
