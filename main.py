
from pathlib import Path

from train_model import (
    train_model,
    FEATURE_COLUMNS,
    LABEL_COLUMNS
)
from localization import localize_issues
from recommendation import recommend_refactorings
from transformation import transform_code
from validation import validate_refactoring
from quality_metrics import compare_metrics


def main():
    print("\n" + "=" * 55)
    print("LLM-GENERATED CODE REFACTORING PIPELINE")
    print("=" * 55)

    # --------------------------------------------------
    # Stage 1: Train the model
    # --------------------------------------------------
    print("\n[1/6] Training model...")

    model, data = train_model()

    print("Model training completed.")
    print("Dataset rows:", len(data))

    # --------------------------------------------------
    # Stage 2: Detect and localize issues
    # --------------------------------------------------
    print("\n[2/6] Detecting and localizing issues...")

    predictions = model.predict(data[FEATURE_COLUMNS])

    localized_issues = localize_issues(
        data,
        predictions,
        LABEL_COLUMNS
    )

    print("Localized issue records:", len(localized_issues))

    # --------------------------------------------------
    # Stage 3: Generate recommendations
    # --------------------------------------------------
    print("\n[3/6] Generating recommendations...")

    results = recommend_refactorings(localized_issues)

    actions_by_line = {}

    for result in results:
        print("\n" + "-" * 55)
        print("Statement ID:", result["statement_id"])
        print("Line:", result["line_no"])
        print("Code:")
        print(result["code"])

        print("\nDetected Issues:")

        for issue in result["detected_issues"]:
            print("  -", issue)

        print("\nRecommended Actions:")

        for recommendation in result["recommendations"]:
            action = recommendation["action"]

            print(
                f"  - {recommendation['refactoring']} "
                f"({action})"
            )

            # Group recommended actions by original source line.
            line_no = int(result["line_no"])

            actions_by_line.setdefault(line_no, [])

            if action not in actions_by_line[line_no]:
                actions_by_line[line_no].append(action)

    # --------------------------------------------------
    # Stage 4: Apply supported transformations
    # --------------------------------------------------
    print("\n[4/6] Applying transformations...")

    source_path = Path("examples.py")

    if not source_path.exists():
        raise FileNotFoundError(
            "examples.py was not found. "
            "Run main.py from the S7_p directory."
        )

    original_code = source_path.read_text(encoding="utf-8")

    transformed_code, applied_actions = transform_code(
        original_code,
        actions_by_line
    )

    print("\n========== APPLIED TRANSFORMATIONS ==========")

    if applied_actions:
        for action in applied_actions:
            print("-", action)
    else:
        print("No supported transformations were applied.")

    print("\n========== TRANSFORMATION SUMMARY ==========")
    print(
        "Recommended action entries:",
        sum(len(actions) for actions in actions_by_line.values())
    )
    print("Transformations applied:", len(applied_actions))

    print("\n========== TRANSFORMED SOURCE CODE ==========")
    print(transformed_code)

    # --------------------------------------------------
    # Stage 5: Validate transformed code
    # --------------------------------------------------
    print("\n[5/6] Validating transformed code...")

    validation_cases = [
        (
            "long_statement_examples",
            [
                (2, 3, 4, 5, 6, 7),
                (5, 4, 3, 2, 1, 6),
                (1, 2, 3, 4, 5, 6),
                (10, 8, 6, 4, 2, 1)
            ]
        ),
        (
            "conditional_examples",
            [
                (2, 1, 0, -1, -2),
                (1, 2, 3, 4, 5),
                (5, 4, 3, 2, 1)
            ]
        ),
        (
            "multiple_issue_examples",
            [
                (2, 3, 4, 5, 6, 7, 3),
                (5, 4, 3, 2, 1, 6, 2),
                (1, 2, 3, 4, 5, 6, 4)
            ]
        )
    ]

    validation_results = []

    for function_name, test_inputs in validation_cases:
        print("\n" + "#" * 55)
        print("Validating function:", function_name)
        print("#" * 55)

        passed = validate_refactoring(
            original_code,
            transformed_code,
            function_name,
            test_inputs
        )

        validation_results.append((function_name, passed))

    print("\n========== OVERALL VALIDATION SUMMARY ==========")

    for function_name, passed in validation_results:
        status = "PASS" if passed else "FAIL"
        print(f"{function_name}: {status}")

    all_passed = all(
        passed for _, passed in validation_results
    )

    print(
        "\nOverall result:",
        "PASS" if all_passed else "FAIL"
    )

    # --------------------------------------------------
    # Stage 6: Evaluate code quality
    # --------------------------------------------------
    print("\n[6/6] Evaluating code quality...")

    compare_metrics(
        original_code,
        transformed_code
    )

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------
    print("\n========== FINAL PIPELINE SUMMARY ==========")
    print("Dataset rows:", len(data))
    print("Localized issue records:", len(localized_issues))
    print(
        "Recommended action entries:",
        sum(len(actions) for actions in actions_by_line.values())
    )
    print("Transformations applied:", len(applied_actions))
    print(
        "Behavioural validation:",
        "PASS" if all_passed else "FAIL"
    )

    print("\n" + "=" * 55)
    print("PIPELINE COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()
