"""
Domain: Scheduling and Resource Allocation
Task: Determine if an employee shift request satisfies strict compliance requirements.
"""

from typing import Dict

def evaluate_shift_eligibility(worker: Dict[str, any], shift: Dict[str, any], station_rating: int) -> bool:
    if (worker.get("hours_worked_week", 0) + shift.get("duration", 8) <= 40 and worker.get("cert_level", 0) >= station_rating and not worker.get("on_leave", False)) or (worker.get("emergency_authorized") is True and shift.get("critical_shortage") is True and worker.get("rest_hours_prior", 0) >= 8) or (shift.get("voluntary_overtime") is True and worker.get("hours_worked_week", 0) < 60 and not shift.get("hazardous", False)):
        return True
    return False

if __name__ == "__main__":
    w = {"hours_worked_week": 32, "cert_level": 3, "on_leave": False}
    s = {"duration": 8, "critical_shortage": False, "voluntary_overtime": False}
    assert evaluate_shift_eligibility(w, s, 2) is True
