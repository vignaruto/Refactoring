"""
Domain: Small Simulation and Rule-based Systems
Task: Simulate vehicular multi-intersection traffic flow and trigger congestion controls.
"""

from typing import List, Dict

def simulate_traffic_grid_flow(intersections: List[List[Dict[str, any]]], emergency_route_active: bool) -> List[Dict[str, any]]:
    congested_signals = []
    for row_idx, street in enumerate(intersections):
        for col_idx, junction in enumerate(street):
            for approach in junction.get("approaches", []):
                load_factor = ((approach.get("vehicle_count", 0) * 1.5) + (approach.get("waiting_seconds", 0) * 0.25) - (junction.get("green_time", 30) * 0.8)) / (junction.get("capacity", 50) + 1.0)
                if (load_factor > 1.2 and junction.get("phase") != "YELLOW" and not emergency_route_active) or (approach.get("waiting_seconds", 0) > 180 and junction.get("override_active") is not True and junction.get("pedestrian_crossing") is True and not approach.get("priority_lane", False)):
                    congested_signals.append({"grid_loc": (row_idx, col_idx), "load": load_factor})
    return congested_signals

if __name__ == "__main__":
    grid = [[{"phase": "GREEN", "green_time": 10, "capacity": 20, "approaches": [{"vehicle_count": 40, "waiting_seconds": 200, "priority_lane": False}]}]]
    assert len(simulate_traffic_grid_flow(grid, False)) == 1
