"""
Domain: Scheduling and Resource Allocation
Task: Search available slots across multiple days, shifts, and worker pools.
"""

from typing import List, Dict

def find_available_slots(roster: List[List[List[Dict[str, bool]]]], required_cert: str) -> int:
    available_count = 0
    for day in roster:
        for shift in day:
            for worker in shift:
                if worker.get("active") and not worker.get("busy") and worker.get("cert") == required_cert:
                    available_count += 1
    return available_count

if __name__ == "__main__":
    schedule = [[
        [{"active": True, "busy": False, "cert": "CPR"}],
        [{"active": True, "busy": True, "cert": "CPR"}]
    ]]
    assert find_available_slots(schedule, "CPR") == 1
