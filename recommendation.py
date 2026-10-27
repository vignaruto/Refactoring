
REFACTORING_ACTIONS = {
    "long_statement": {
        "name": "Decompose Expression",
        "action": "DECOMPOSE_EXPRESSION"
    },
    "nested_loop": {
        "name": "Restructure Nested Loop",
        "action": "RESTRUCTURE_LOOP"
    },
    "complex_conditional": {
        "name": "Extract Condition",
        "action": "EXTRACT_CONDITION"
    }
}


def get_recommendations(detected_issues):
    """
    Convert detected issue labels into structured
    refactoring recommendations.
    """

    recommendations = []

    for issue in detected_issues:
        recommendation = REFACTORING_ACTIONS.get(issue)

        if recommendation:
            recommendations.append({
                "issue": issue,
                "refactoring": recommendation["name"],
                "action": recommendation["action"]
            })

    return recommendations


def recommend_refactorings(localized_issues):
    """
    Generate recommendations for all localized statements.
    """

    results = []

    for statement in localized_issues:
        recommendations = get_recommendations(
            statement["detected_issues"]
        )

        results.append({
            **statement,
            "recommendations": recommendations
        })

    return results


if __name__ == "__main__":
    # Small demonstration of the recommendation stage.
    example_issues = [
        {
            "statement_id": 4,
            "line_no": 12,
            "code": "result = a * b + c * d",
            "detected_issues": ["long_statement"]
        },
        {
            "statement_id": 6,
            "line_no": 19,
            "code": "if a > b and b > c:",
            "detected_issues": ["complex_conditional"]
        }
    ]

    for result in recommend_refactorings(example_issues):
        print("-" * 40)
        print("Statement ID:", result["statement_id"])
        print("Line:", result["line_no"])
        print("Detected Issues:", result["detected_issues"])
        print("Recommendations:")

        for recommendation in result["recommendations"]:
            print(
                f"  - {recommendation['refactoring']} "
                f"({recommendation['action']})"
            )
