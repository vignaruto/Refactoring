def column_quality(values, allowed=None):
    total = len(values)
    blanks = sum(1 for v in values if v in (None, ""))
    distinct = len({v for v in values if v not in (None, "")})
    invalid = sum(1 for v in values if allowed and v not in (None, "") and v not in allowed)
    if total and blanks / total < 0.05 and invalid == 0 or distinct == 1:
        grade = "A"
    elif blanks / max(total, 1) < 0.2:
        grade = "B"
    else:
        grade = "C"
    return grade, round(1 - (blanks + invalid) / max(total, 1), 3), distinct

if __name__ == "__main__":
    assert column_quality(["a", "b", "a"], {"a", "b"}) == ("A", 1.0, 2)
    messy = ["a", "", "x", None, "a"]
    assert column_quality(messy, {"a"}) == ("C", 0.4, 2)
