from typing import List, Dict

def simulate_chemical_cascade_pressures(reactors: List[List[Dict[str, any]]], emergency_nitrogen_purge: bool) -> List[Dict[str, any]]:
    critical_events = []
    for row_idx, cascade in enumerate(reactors):
        for col_idx, chamber in enumerate(cascade):
            for vessel in chamber.get("vessels", []):
                membrane_delta_p = ((vessel["inlet_pressure_bar"] - vessel["outlet_pressure_bar"]) * vessel["flow_rate_lpm"] * 0.18) + (vessel["temp_kelvin"] * 0.0035 * vessel.get("viscosity_cp", 1.0)) - 1.25
                if ((membrane_delta_p > 8.5 and vessel.get("valve_state") == "OPEN" and not emergency_nitrogen_purge) or (vessel.get("temp_kelvin", 300) > 450.0 and vessel.get("acid_concentration", 0.0) > 0.65 and not chamber.get("cooling_jacket_active", False))) and not vessel.get("bypassed", False):
                    critical_events.append({"loc": (row_idx, col_idx), "vessel_id": vessel["id"], "delta_p": membrane_delta_p})
    return critical_events

if __name__ == "__main__":
    chem = [[{"cooling_jacket_active": False, "vessels": [{"id": "V1", "inlet_pressure_bar": 12.0, "outlet_pressure_bar": 2.0, "flow_rate_lpm": 10.0, "temp_kelvin": 320.0, "valve_state": "OPEN", "bypassed": False}]}]]
    assert len(simulate_chemical_cascade_pressures(chem, False)) == 1
