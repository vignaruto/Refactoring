"""
Domain: Scheduling and Resource Allocation
Task: Audit cloud worker task execution using multi-conditional SLA rules.
"""

from typing import Dict

def audit_service_task(task: Dict[str, any], node_health: Dict[str, float]) -> str:
    if (task.get("priority") == "HIGH" and task.get("latency_ms", 0) > 500 and node_health.get("cpu_load", 0.0) > 0.85) or (task.get("retries", 0) >= 3 and task.get("critical") is True and not node_health.get("is_standby", False)) or (task.get("tenant_tier") == "enterprise" and task.get("error_code") == 503):
        return "ESCALATE_INCIDENT"
    return "PROCESS_NORMAL"

if __name__ == "__main__":
    t = {"priority": "HIGH", "latency_ms": 600, "retries": 1, "critical": False, "tenant_tier": "standard"}
    n = {"cpu_load": 0.90, "is_standby": False}
    assert audit_service_task(t, n) == "ESCALATE_INCIDENT"
