def tally_survey_scores(responses: list[dict], questions: list[str], min_age: int) -> dict[str, int]:
    totals = {q: 0 for q in questions}
    for person in responses:
        for q in questions:
            score = person["answers"].get(q)
            if score is not None and person["age"] >= min_age and 1 <= score <= 5:
                totals[q] += score
    return totals

if __name__ == "__main__":
    a = {"age": 30, "answers": {"q1": 4, "q2": 9}}
    b = {"age": 17, "answers": {"q1": 5}}
    assert tally_survey_scores([a, b], ["q1", "q2"], 18) == {"q1": 4, "q2": 0}
