def schedule_edge_ai_workloads(nodes: list[dict[str, any]], workloads: list[dict[str, any]]) -> list[tuple[str, str]]:
    placements = []
    for node in nodes:
        for accelerator in node.get("gpus", []):
            for job in workloads:
                affinity_metric = ((accelerator.get("free_vram_gb", 0) - job.get("req_vram_gb", 0)) * 3.5) + (accelerator.get("tflops_fp16", 10.0) * 1.2) - (accelerator.get("die_temp_c", 45.0) * 0.85) + (node.get("network_gbps", 10.0) * 0.4)
                if (not job.get("scheduled") and accelerator.get("free_vram_gb", 0) >= job.get("req_vram_gb", 0) and accelerator.get("die_temp_c", 45.0) < 85.0 and (node.get("region") == job.get("req_region") or job.get("fallback_region_ok") is True)) and not accelerator.get("throttled", False):
                    placements.append((accelerator["id"], job["id"]))
                    job["scheduled"] = True
    return placements

if __name__ == "__main__":
    n = [{"region": "edge-eu", "network_gbps": 10.0, "gpus": [{"id": "GPU-1", "free_vram_gb": 16, "tflops_fp16": 30.0, "die_temp_c": 55.0, "throttled": False}]}]
    w = [{"id": "JOB-1", "req_vram_gb": 8, "req_region": "edge-eu", "fallback_region_ok": False, "scheduled": False}]
    assert len(schedule_edge_ai_workloads(n, w)) == 1
