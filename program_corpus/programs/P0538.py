def course_final_score(quizzes: list[float], midterm: float, final: float, project: float) -> float:
    quiz_avg = sum(quizzes) / len(quizzes) if quizzes else 0.0
    return round(quiz_avg * 0.15 + midterm * 0.25 + final * 0.4 + project * 0.2, 1)

if __name__ == "__main__":
    assert abs(course_final_score([80, 100], 60, 80, 90) - 78.5) < 0.06
    assert course_final_score([], 0, 0, 0) == 0.0
