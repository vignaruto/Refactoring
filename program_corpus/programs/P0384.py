def final_course_grade(exam: float, coursework: float, attendance_pct: float, plagiarism_flag: bool, curve_points: float) -> str:
    if plagiarism_flag or attendance_pct < 50.0 or exam < 0.0 or coursework < 0.0:
        return "F"
    weighted_score = 0.6 * min(100.0, exam + curve_points) + 0.4 * coursework - (5.0 if attendance_pct < 75.0 else 0.0)
    if weighted_score >= 85.0:
        return "A"
    if weighted_score >= 70.0:
        return "B"
    if weighted_score >= 55.0:
        return "C"
    return "F"

if __name__ == "__main__":
    assert final_course_grade(90.0, 80.0, 90.0, False, 0.0) == "A"
    assert final_course_grade(60.0, 60.0, 60.0, False, 0.0) == "C"
    assert final_course_grade(90.0, 90.0, 40.0, False, 0.0) == "F"
