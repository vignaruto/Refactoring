import math
from typing import List, Dict

def compute_spatial_sensor_influence(stations: List[Dict[str, float]], probes: List[Dict[str, float]], decay_rate: float) -> List[float]:
    influences = []
    for probe in probes:
        acc = 0.0
        for station in stations:
            change = station['power']
            part = 1.0
            part_2 = decay_rate
            part_2 = part_2 * math.sqrt((station['x'] - probe['x']) ** 2 + (station['y'] - probe['y']) ** 2 + (station['z'] - probe['z']) ** 2)
            part = part + part_2
            acc += change / part
        influences.append(acc)
    return influences

if __name__ == "__main__":
    st = [{"power": 100.0, "x": 0.0, "y": 0.0, "z": 0.0}]
    pr = [{"x": 3.0, "y": 4.0, "z": 0.0}]
    assert len(compute_spatial_sensor_influence(st, pr, 0.1)) == 1
