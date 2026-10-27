
from pathlib import Path

from train_model import train_model
from localization import localize_file, localize_test_programs
from recommendation import recommend_refactorings
from transformation import automatable_targets, transform_source
from validation import validate_program
from quality_metrics import compare_metrics


def main():
    print("\n" + "=" * 55)
    print("LLM-GENERATED CODE REFACTORING PIPELINE")
    print("=" * 55)

    # --------------------------------------------------
    # Stage 1: Train the model
    # --------------------------------------------------
    print("\n[1/6] Training model...")

    model, data, train, test = train_model()

    print("Model training completed.")
    print("Dataset rows:", len(data))
    print("Training rows:", int(train.sum()))

    # --------------------------------------------------
    # Stage 2: Detect and localize issues
    # --------------------------------------------------
    print("\n[2/6] Detecting and localizing issues...")

    # Evaluation runs only on the held-out programs the model never saw.
    _, _, evaluation = localize_test_programs(model, data, test)

    print("Held-out programs:", evaluation["programs"])
    print("Issues localized:", evaluation["issues"])
    for label, m in evaluation["statement_level"].items():
        print(f"  {label}: P={m['precision']:.3f} "
              f"R={m['recall']:.3f} F1={m['f1']:.3f}")
    print(
        "Programs localized exactly:",
        f"{evaluation['programs_localized_exactly']}/{evaluation['programs']}"
    )

    # The remaining stages run on one file, so line numbers are unambiguous.
    source_path = Path(__file__).resolve().parent / "examples.py"
    localized_issues, _ = localize_file(model, source_path)

    print(f"\nLocalized issue records in {source_path.name}:",
          len(localized_issues))

    # --------------------------------------------------
    # Stage 3: Generate recommendations
    # --------------------------------------------------
    print("\n[3/6] Generating recommendations...")

    original_code = source_path.read_text(encoding="utf-8")
    results = recommend_refactorings(
        localized_issues, lambda issue: original_code
    )

    targets = []

    for result in results:
        print("\n" + "-" * 55)
        print("Statement ID:", result["statement_id"])
        print("Line:", result["line_no"])
        print("Code:")
        print(result["code"])

        print("\nRecommended Actions:")

        for recommendation in result["recommendations"]:
            action = recommendation["action"]
            severity = recommendation["severity"]

            print(
                f"  - {recommendation['issue']}: "
                f"{recommendation['refactoring']} ({action})"
            )
            print(
                f"    {severity['measure']} = {severity['value']} "
                f"(flagged from {severity['flagged_at']})"
            )

            if not recommendation["automatable"]:
                print(f"    Not automatic: {recommendation['reason']}")

        targets += automatable_targets(result)

    # --------------------------------------------------
    # Stage 4: Apply supported transformations
    # --------------------------------------------------
    print("\n[4/6] Applying transformations...")

    transformed_code, outcomes = transform_source(original_code, targets)
    applied_actions = [o for o in outcomes if o["status"] == "applied"]

    print("\n========== TRANSFORMATION OUTCOMES ==========")

    for outcome in outcomes:
        detail = f" ({outcome['detail']})" if outcome["detail"] else ""
        print(f"- line {outcome['line_no']}: {outcome['action']} "
              f"{outcome['status']}{detail}")

    print("\n========== TRANSFORMATION SUMMARY ==========")
    print("Automatable action entries:", len(targets))
    print("Transformations applied:", len(applied_actions))

    print("\n========== TRANSFORMED SOURCE CODE ==========")
    print(transformed_code)

    # --------------------------------------------------
    # Stage 5: Validate transformed code
    # --------------------------------------------------
    print("\n[5/6] Validating transformed code...")

    # examples.py has no self-test, so the calls to compare are given here;
    # stage 9 adds edge-case variants of each.
    validation_calls = [
        ["long_statement_examples", [2, 3, 4, 5, 6, 7]],
        ["long_statement_examples", [10, 8, 6, 4, 2, 1]],
        ["conditional_examples", [2, 1, 0, -1, -2]],
        ["conditional_examples", [1, 2, 3, 4, 5]],
        ["nested_loop_examples", [3]],
        ["multiple_issue_examples", [2, 3, 4, 5, 6, 7, 3]],
        ["multiple_issue_examples", [5, 4, 3, 2, 1, 6, 2]],
    ]

    report = validate_program(
        original_code, transformed_code, validation_calls
    )
    differential = report.get("differential", {})

    print("Syntax valid:", not report["syntax_error"])
    print("Safety problems:", report.get("safety_problems") or "none")
    print("Calls compared (with edge-case variants):",
          differential.get("calls", 0))
    print("Mismatches:", len(differential.get("mismatches", [])))
    for mismatch in differential.get("mismatches", [])[:5]:
        print(f"  {mismatch['function']}{mismatch['args']}: "
              f"original {mismatch['original']}, "
              f"transformed {mismatch['transformed']}")

    all_passed = report["valid"]

    print(
        "\nOverall result:",
        "PASS" if all_passed else "FAIL"
    )
    for reason in report["reasons"]:
        print("  -", reason)

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
        "Automatable action entries:",
        len(targets)
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
