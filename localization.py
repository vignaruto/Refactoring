"""
localization.py
Stage 6 of the pipeline: detection and localization.

Runs the trained detector on statement records and turns its positive
predictions into issue locations: program, file, line span, statement type,
source text, issue labels and the model's confidence for each label.

- A prediction is kept only for statement types the issue can occur on
  (long_statement on simple statements, nested_loop on loop headers,
  complex_conditional on if/elif/while tests); the rest are dropped and
  counted.
- Every location is checked against its source file: the recorded line
  span must contain the statement's source text.
- On the held-out test programs, predicted locations are compared with the
  labelled ones per statement and per program.
- localize_file() runs the same detection on any Python file.

Outputs (written to results/):
  localized_issues.json        issues per held-out program
  localization_evaluation.json statement- and program-level scores
"""

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

from generate_dataset import extract_statements
from train_model import LABEL_COLUMNS, build_features, train_model

BASE_DIR = Path(__file__).resolve().parent
PROGRAMS_DIR = BASE_DIR / "program_corpus" / "programs"
RESULTS_DIR = BASE_DIR / "results"

SIMPLE_TYPES = {"Assign", "AnnAssign", "AugAssign", "Expr", "Return"}
LOOP_TYPES = {"For", "AsyncFor", "While"}
ISSUE_STATEMENT_TYPES = {
    "long_statement": SIMPLE_TYPES,
    "nested_loop": LOOP_TYPES,
    "complex_conditional": {"If", "While"},
}


def detect(model, data):
    """Predicted labels and positive-class probabilities, one column per label."""
    features = build_features(data)
    predictions = np.asarray(model.predict(features))
    probabilities = np.zeros(predictions.shape)
    for i, (estimator, proba) in enumerate(
        zip(model.estimators_, model.predict_proba(features))
    ):
        classes = list(estimator.classes_)
        if 1 in classes:
            probabilities[:, i] = proba[:, classes.index(1)]
    return predictions, probabilities


def localize_issues(data, predictions, probabilities=None,
                    label_columns=LABEL_COLUMNS):
    """
    Return (issues, dropped).

    issues has one entry per statement with at least one kept issue.
    dropped lists positive predictions on statement types the issue
    cannot occur on.
    """
    issues, dropped = [], []
    for index, statement in enumerate(data.to_dict("records")):
        detected, confidence = [], {}
        for i, label in enumerate(label_columns):
            if predictions[index][i] != 1:
                continue
            location = {
                "program_id": statement.get("program_id", ""),
                "line_no": int(statement["line_no"]),
                "label": label,
            }
            if statement["statement_type"] not in ISSUE_STATEMENT_TYPES[label]:
                dropped.append(location)
                continue
            detected.append(label)
            if probabilities is not None:
                confidence[label] = round(float(probabilities[index][i]), 4)
        if detected:
            issues.append({
                "program_id": statement.get("program_id", ""),
                "filename": statement.get("filename", ""),
                "statement_id": int(statement["statement_id"]),
                "line_no": int(statement["line_no"]),
                "end_line": int(statement["end_line"]),
                "statement_type": statement["statement_type"],
                "in_main_guard": int(statement["in_main_guard"]),
                "code": statement["code"],
                "detected_issues": detected,
                "confidence": confidence,
            })
    return issues, dropped


def verify_locations(issues, source_for):
    """Issues whose line span does not contain their source text."""
    problems = []
    for issue in issues:
        lines = source_for(issue).splitlines(keepends=True)
        span = "".join(lines[issue["line_no"] - 1:issue["end_line"]])
        if not lines or issue["code"] not in span:
            problems.append(
                f"{issue['program_id'] or issue['filename']} line "
                f"{issue['line_no']}: span does not contain the statement"
            )
    return problems


def program_source(issue, programs_dir=PROGRAMS_DIR):
    return (programs_dir / issue["filename"]).read_text(encoding="utf-8")


def scores(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": round(precision, 4), "recall": round(recall, 4),
        "f1": round(f1, 4), "tp": tp, "fp": fp, "fn": fn,
    }


def evaluate_localization(data, issues, label_columns=LABEL_COLUMNS):
    """Compare predicted issue locations with the labelled ones."""
    predicted = {
        (issue["program_id"], issue["statement_id"], label)
        for issue in issues for label in issue["detected_issues"]
    }
    truth = {
        (row["program_id"], int(row["statement_id"]), label)
        for row in data.to_dict("records")
        for label in label_columns if row[label] == 1
    }
    statement_level = {}
    program_level = {}
    for label in label_columns:
        pred = {key for key in predicted if key[2] == label}
        true = {key for key in truth if key[2] == label}
        statement_level[label] = scores(
            len(pred & true), len(pred - true), len(true - pred)
        )
        pred_programs = {key[0] for key in pred}
        true_programs = {key[0] for key in true}
        program_level[label] = scores(
            len(pred_programs & true_programs),
            len(pred_programs - true_programs),
            len(true_programs - pred_programs),
        )

    programs = sorted(data["program_id"].unique())
    exact = sum(
        {key for key in predicted if key[0] == pid}
        == {key for key in truth if key[0] == pid}
        for pid in programs
    )
    code_by_key = {
        (row["program_id"], int(row["statement_id"])): (
            int(row["line_no"]), row["code"]
        )
        for row in data.to_dict("records")
    }
    errors = [
        {
            "kind": kind, "program_id": pid, "line_no": code_by_key[(pid, sid)][0],
            "label": label, "code": code_by_key[(pid, sid)][1],
        }
        for kind, keys in (("missed", truth - predicted), ("false_alarm", predicted - truth))
        for pid, sid, label in sorted(keys)
    ]
    return {
        "statement_level": statement_level,
        "program_level": program_level,
        "programs": len(programs),
        "programs_localized_exactly": int(exact),
        "errors": errors,
    }


def statements_for_file(path):
    """Statement records for any Python file, in dataset column format."""
    path = Path(path)
    source = path.read_text(encoding="utf-8")
    records = extract_statements(ast.parse(source), source.splitlines(keepends=True))
    data = pd.DataFrame(records)
    data["program_id"] = ""
    data["filename"] = path.name
    return data


def localize_file(model, path):
    """Detect and localize issues in one Python file; return (issues, dropped)."""
    data = statements_for_file(path)
    predictions, probabilities = detect(model, data)
    issues, dropped = localize_issues(data, predictions, probabilities)
    source = Path(path).read_text(encoding="utf-8")
    problems = verify_locations(issues, lambda issue: source)
    if problems:
        raise RuntimeError("Bad issue locations:\n" + "\n".join(problems))
    return issues, dropped


def localize_test_programs(model, data, test):
    """Run stage 6 on the held-out programs; return (issues, dropped, evaluation)."""
    test_data = data[test].reset_index(drop=True)
    predictions, probabilities = detect(model, test_data)
    issues, dropped = localize_issues(test_data, predictions, probabilities)
    problems = verify_locations(issues, program_source)
    if problems:
        raise RuntimeError("Bad issue locations:\n" + "\n".join(problems))
    evaluation = evaluate_localization(test_data, issues)
    evaluation["dropped_type_mismatches"] = len(dropped)
    evaluation["issue_statements"] = len(issues)
    evaluation["issues"] = sum(len(issue["detected_issues"]) for issue in issues)
    return issues, dropped, evaluation


def group_by_program(issues):
    grouped = {}
    for issue in issues:
        entry = grouped.setdefault(
            issue["program_id"], {"filename": issue["filename"], "issues": []}
        )
        entry["issues"].append({
            key: value for key, value in issue.items()
            if key not in ("program_id", "filename")
        })
    return grouped


def main():
    model, data, _, test = train_model()
    issues, dropped, evaluation = localize_test_programs(model, data, test)

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "localized_issues.json").write_text(
        json.dumps(group_by_program(issues), indent=2), encoding="utf-8"
    )
    (RESULTS_DIR / "localization_evaluation.json").write_text(
        json.dumps(evaluation, indent=2), encoding="utf-8"
    )

    print(f"Held-out programs: {evaluation['programs']}")
    print(f"Issues localized: {evaluation['issues']} on "
          f"{evaluation['issue_statements']} statements "
          f"(all spans verified against the program files)")
    print(f"Dropped type-mismatched predictions: {len(dropped)}")
    for level in ("statement_level", "program_level"):
        print(f"\n{level.replace('_', ' ').capitalize()}:")
        for label, m in evaluation[level].items():
            print(f"  {label:20s} P={m['precision']:.3f} R={m['recall']:.3f} "
                  f"F1={m['f1']:.3f}  (TP={m['tp']} FP={m['fp']} FN={m['fn']})")
    print(f"\nPrograms localized exactly: "
          f"{evaluation['programs_localized_exactly']}/{evaluation['programs']}")
    for error in evaluation["errors"]:
        print(f"  {error['kind']:11s} {error['program_id']} line "
              f"{error['line_no']} {error['label']}: {error['code'][:60]}")
    print(f"\nSaved results to {RESULTS_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    main()
