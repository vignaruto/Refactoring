"""
Domain: Data Aggregation and Statistics
Task: Multi-factor student grade qualification check.
"""

from typing import Dict, List

def qualify_honor_student(grades: List[float], attendance_rate: float, discipline: Dict[str, int]) -> bool:
    if (len(grades) >= 5 and sum(grades) / len(grades) >= 90.0 and attendance_rate >= 0.95 and discipline.get("suspensions", 0) == 0) or (attendance_rate >= 0.98 and min(grades) >= 80.0 and discipline.get("warnings", 0) <= 1 and discipline.get("service_hours", 0) >= 50):
        return True
    return False

if __name__ == "__main__":
    g = [92.0, 95.0, 88.0, 94.0, 91.0]
    d = {"suspensions": 0, "warnings": 0, "service_hours": 20}
    assert qualify_honor_student(g, 0.96, d) is True
