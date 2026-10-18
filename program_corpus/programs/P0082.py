from typing import List, Dict

def compute_processor_task_delays(nodes: List[Dict[str, float]], tasks: List[Dict[str, float]], network_overhead: float) -> List[List[float]]:
    latencies = []
    for node in nodes:
        row = []
        for task in tasks:
            turnaround_time = (task["payload_mb"] / node["bandwidth_mbps"]) + (task["cycles_giga"] / node["clock_ghz"] * node["ipc_efficiency"]) + network_overhead
            row.append(turnaround_time)
        latencies.append(row)
    return latencies

if __name__ == "__main__":
    n = [{"bandwidth_mbps": 100.0, "clock_ghz": 3.0, "ipc_efficiency": 1.2}]
    t = [{"payload_mb": 50.0, "cycles_giga": 6.0}]
    assert len(compute_processor_task_delays(n, t, 0.05)) == 1
