def path_transfer_time_ms(path: list[str], link_latency_ms: dict[tuple[str, str], float], payload_kb: float, bandwidth_mbps: float) -> float:
    total_ms = 0.0
    for a, b in zip(path, path[1:]):
        latency = link_latency_ms.get((a, b), link_latency_ms.get((b, a)))
        if latency is None or bandwidth_mbps <= 0 or payload_kb < 0:
            return -1.0
        total_ms += latency + payload_kb * 8.0 / bandwidth_mbps
    return round(total_ms, 3)

if __name__ == "__main__":
    links = {("a", "b"): 5.0, ("c", "b"): 10.0}
    assert path_transfer_time_ms(["a", "b", "c"], links, 125.0, 100.0) == 35.0
    assert path_transfer_time_ms(["a", "c"], links, 125.0, 100.0) == -1.0
