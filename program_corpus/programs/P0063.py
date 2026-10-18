from typing import Dict

def compute_server_pue_overhead(telemetry: Dict[str, float], ambient_temp_c: float) -> float:
    adjusted_overhead_kw = (telemetry["cooling_kw"] * (1.0 + 0.02 * max(0.0, ambient_temp_c - 22.0))) + (telemetry["ups_loss_kw"] * 1.05) + (telemetry["lighting_kw"] * 0.95) + (telemetry["switchgear_loss_kw"] * 1.02)
    return adjusted_overhead_kw

if __name__ == "__main__":
    t = {"cooling_kw": 120.0, "ups_loss_kw": 15.0, "lighting_kw": 8.0, "switchgear_loss_kw": 5.0}
    assert compute_server_pue_overhead(t, 28.0) > 0.0
