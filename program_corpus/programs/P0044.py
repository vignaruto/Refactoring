"""
Domain: Small Simulation and Rule-based Systems
Task: Simulate packet buffer queue drop and latency accumulation.
"""

from typing import List, Dict

def simulate_network_queue(packets: List[Dict[str, float]], max_buffer_size: int, drain_rate: float) -> Dict[str, float]:
    buffer_used = 0.0
    dropped = 0
    total_latency = 0.0
    for pkt in packets:
        buffer_used = max(0.0, buffer_used - drain_rate)
        if buffer_used + pkt["size"] <= max_buffer_size:
            buffer_used += pkt["size"]
            total_latency += buffer_used / drain_rate
        else:
            dropped += 1
    return {"dropped": dropped, "total_latency": total_latency}

if __name__ == "__main__":
    pkts = [{"size": 10.0}, {"size": 20.0}, {"size": 30.0}]
    stats = simulate_network_queue(pkts, 25, 5.0)
    assert stats["dropped"] >= 1
