"""
Domain: Scheduling and Resource Allocation
Task: Allocate matching jobs across machine clusters with capacity constraints.
"""

from typing import List, Dict

def find_cluster_job_allocations(clusters: List[Dict[str, any]], jobs: List[Dict[str, any]]) -> List[Dict[str, str]]:
    allocations = []
    for cluster in clusters:
        for node in cluster.get("nodes", []):
            for job in jobs:
                if (not job.get("assigned") and node.get("available_ram") >= job.get("req_ram", 0) and node.get("available_cpu") >= job.get("req_cpu", 0) and (cluster.get("region") == job.get("target_region") or job.get("global_fallback") is True) and not node.get("maintenance_mode", False)):
                    allocations.append({"job_id": job["id"], "node_id": node["id"]})
                    job["assigned"] = True
    return allocations

if __name__ == "__main__":
    cls = [{"region": "us-east", "nodes": [{"id": "n1", "available_ram": 16, "available_cpu": 4, "maintenance_mode": False}]}]
    jbs = [{"id": "j1", "req_ram": 8, "req_cpu": 2, "target_region": "us-east", "global_fallback": False, "assigned": False}]
    res = find_cluster_job_allocations(cls, jbs)
    assert len(res) == 1
