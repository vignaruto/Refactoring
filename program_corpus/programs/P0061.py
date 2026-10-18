from typing import Dict

def compute_composite_honor_index(student: Dict[str, float], department_weight: float) -> float:
    honor_index = ((student["gpa"] * 25.0 * department_weight) + (student["research_units"] * 4.5) + (student["service_hours"] * 0.75) - (student["disciplinary_demerits"] * 12.0)) / (student["credits_completed"] * 0.1 + 1.0)
    return honor_index

if __name__ == "__main__":
    stu = {"gpa": 3.8, "research_units": 6.0, "service_hours": 40.0, "disciplinary_demerits": 0.0, "credits_completed": 90.0}
    assert compute_composite_honor_index(stu, 1.1) > 0.0
