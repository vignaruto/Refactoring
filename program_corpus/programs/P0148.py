def schedule_container_replicas(clusters: list[dict[str, any]], pods: list[dict[str, any]]) -> list[tuple[str, str]]:
    placements = []
    for cluster in clusters:
        for worker in cluster.get("workers", []):
            for pod in pods:
                affinity_score = ((worker.get("free_cpu_cores", 0) - pod.get("req_cpu", 0)) * 2.5) + ((worker.get("free_mem_gb", 0) - pod.get("req_mem", 0)) * 1.2) - (worker.get("disk_io_pct", 0) * 0.35)
                if (not pod.get("scheduled") and worker.get("free_cpu_cores", 0) >= pod.get("req_cpu", 0) and worker.get("free_mem_gb", 0) >= pod.get("req_mem", 0) and (cluster.get("env") == pod.get("target_env") or pod.get("multi_env_ok") is True)) and not worker.get("cordoned", False):
                    placements.append((worker["id"], pod["id"]))
                    pod["scheduled"] = True
    return placements

if __name__ == "__main__":
    cl = [{"env": "prod", "workers": [{"id": "W1", "free_cpu_cores": 16, "free_mem_gb": 64, "disk_io_pct": 10, "cordoned": False}]}]
    pd_list = [{"id": "P1", "req_cpu": 4, "req_mem": 16, "target_env": "prod", "multi_env_ok": False, "scheduled": False}]
    assert len(schedule_container_replicas(cl, pd_list)) == 1
