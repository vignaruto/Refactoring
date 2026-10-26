def response_quality(answers, seconds_taken, attention_check):
    distinct = len(set(answers))
    if seconds_taken < 30 or attention_check != "blue" or distinct == 1 and len(answers) > 5:
        return "reject"
    if seconds_taken < 60:
        return "review"
    return "accept"

if __name__ == "__main__":
    assert response_quality([3, 3, 3, 3, 3, 3], 100, "blue") == "reject"
    assert response_quality([1, 2, 3], 45, "blue") == "review"
    assert response_quality([1, 2], 90, "blue") == "accept"
    assert response_quality([1], 90, "red") == "reject"
