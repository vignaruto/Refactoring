def autoscale_replicas(cpu_pct: float, queue_depth: int, replicas: int, min_r: int = 2, max_r: int = 20) -> int:
    pressure = max(cpu_pct / 70.0, queue_depth / max(1, replicas * 50))
    desired = max(min_r, min(max_r, int(replicas * pressure + 0.999)))
    if cpu_pct < 30.0 and queue_depth == 0 and replicas > min_r:
        return max(min_r, replicas - 1)
    return desired

if __name__ == "__main__":
    assert autoscale_replicas(35.0, 0, 4) == 2
    assert autoscale_replicas(20.0, 0, 4) == 3
    assert autoscale_replicas(140.0, 0, 4) == 8
