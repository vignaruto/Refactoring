"""
main.py
Runs stages 5-10 of the pipeline once, on the held-out test programs,
and prints a short report per stage.

  5  train the detector on the training programs
  6  detect and localize issues in the held-out programs
  7  recommend a refactoring for each issue
  8  apply the automatable refactorings
  9  validate each refactored program (rejected ones keep their original)
 10  compare the programs before and after

Writes results/validated_programs/ (the final programs) and
results/pipeline_summary.json. Each stage's own script (train_model.py,
localization.py, ..., quality_metrics.py) writes its detailed results.
"""

import json
from pathlib import Path

import quality_metrics
import recommendation
import transformation
import validation
from localization import localize_test_programs, program_source
from train_model import LABEL_COLUMNS, build_features, label_metrics, train_model

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"


def heading(number, title):
    print(f"\n[Stage {number}] {title}")


def main():
    print("=" * 60)
    print("REFACTORING PIPELINE FOR LLM-GENERATED CODE")
    print("=" * 60)

    heading(5, "Training the issue detector")
    model, data, train, test = train_model()
    test_rows = data[test]
    detector = label_metrics(
        test_rows[LABEL_COLUMNS].to_numpy(), model.predict(build_features(test_rows))
    )
    print(f"Training: {data.loc[train, 'program_id'].nunique()} programs, "
          f"{int(train.sum())} statements")
    print(f"Held out: {test_rows['program_id'].nunique()} programs, "
          f"{int(test.sum())} statements")
    for label, m in detector.items():
        print(f"  {label:20s} F1 {m['f1']:.3f}")

    heading(6, "Detecting and localizing issues")
    issues, dropped, localization = localize_test_programs(model, data, test)
    print(f"Issues localized: {localization['issues']} "
          f"(type-mismatched predictions dropped: {len(dropped)})")
    for label, m in localization["statement_level"].items():
        print(f"  {label:20s} P {m['precision']:.3f}  R {m['recall']:.3f}")
    print(f"Programs localized exactly: "
          f"{localization['programs_localized_exactly']}/{localization['programs']}")

    heading(7, "Recommending refactorings")
    recommendations = recommendation.recommend_refactorings(issues)
    recommended = recommendation.summarize(recommendations)
    print(f"Recommendations: {recommended['recommendations']}, "
          f"automatable: {recommended['automatable']}, "
          f"in __main__ (left unchanged): {recommended['in_main_guard']}")
    for action, counts in recommended["by_action"].items():
        print(f"  {action:32s} {counts['count']:4d} ({counts['automatable']} automatable)")

    heading(8, "Applying refactorings")
    transformations = transformation.transform_programs(recommendations, program_source)
    transformed = transformation.summarize(transformations)
    print(f"Programs transformed: {transformed['programs_transformed']}, "
          f"outcomes: {transformed['status']}")
    for reason, count in transformed["skip_reasons"].items():
        print(f"  skipped {count}: {reason}")

    heading(9, "Validating refactored programs")
    reports = validation.validate_programs(transformations)
    validated = validation.summarize(reports)
    print(f"Valid: {validated['valid']}/{validated['programs']}, "
          f"self-tests passed: {validated['self_tests_passed']}, "
          f"differential calls: {validated['differential_calls']}, "
          f"mismatches: {validated['differential_mismatches']}")
    for pid in validated["rejected"]:
        print(f"  rejected {pid}: {'; '.join(reports[pid]['reasons'])}")

    heading(10, "Comparing before and after")
    before, after, changed = quality_metrics.final_programs(test_rows, transformations, reports)
    table, resolution = quality_metrics.evaluate(model, before, after, changed)
    stats = quality_metrics.metric_statistics(table)
    funnel = quality_metrics.funnel(issues, recommendations, transformations, reports)
    print("Target issues outside __main__ (before -> after):")
    for label, r in resolution.items():
        print(f"  {label:20s} {r['before']:4d} -> {r['after']:4d}  "
              f"resolved {r['resolution_rate']:.0%}, introduced {r['introduced']}")
    print("Quality metrics (mean before -> after, programs better / worse):")
    for metric, s in stats.items():
        print(f"  {metric:28s} {s['mean_before']:8.2f} -> {s['mean_after']:8.2f}  "
              f"{s['programs_better']:3d} / {s['programs_worse']:3d}")

    validation_dir = validation.VALIDATED_DIR
    validation_dir.mkdir(parents=True, exist_ok=True)
    for old in validation_dir.glob("*.py"):
        old.unlink()
    for pid, source in after.items():
        (validation_dir / f"{pid}.py").write_text(source, encoding="utf-8")
    summary = {
        "detector_test_f1": {label: m["f1"] for label, m in detector.items()},
        "localization": {k: v for k, v in localization.items() if k != "errors"},
        "recommendation": recommended,
        "transformation": transformed,
        "validation": validated,
        "funnel": funnel,
        "issue_resolution": resolution,
        "metrics": stats,
    }
    (RESULTS_DIR / "pipeline_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("\nPipeline funnel:")
    for step, count in funnel.items():
        print(f"  {step:32s} {count}")
    print(f"\nFinal programs: {validation_dir.relative_to(BASE_DIR)}/ | "
          f"summary: {(RESULTS_DIR / 'pipeline_summary.json').relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
