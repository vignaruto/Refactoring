"""
train_model.py
Stage 5 of the pipeline: supervised learning on dataset.csv.

- Program-level train/test split: whole similarity groups go to one side,
  so a program (and its near-duplicates) is never in both. The split is
  stratified by intended_category so every category is in the test set.
- Multi-output Random Forest predicting long_statement, nested_loop and
  complex_conditional for each statement record.
- Evaluation: per-label precision/recall/F1 and confusion counts on the
  held-out programs, exact-match accuracy, grouped 5-fold cross-validation,
  and a cross-model check (train on one generating LLM, test on the other).

Outputs (written to results/):
  model_evaluation.json  all metrics
  test_predictions.csv   held-out statements with true and predicted labels
  feature_importance.csv mean impurity importance per feature
The trained model is saved to models/issue_detector.joblib.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    hamming_loss,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.multioutput import MultiOutputClassifier

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
RESULTS_DIR = BASE_DIR / "results"
MODEL_PATH = BASE_DIR / "models" / "issue_detector.joblib"

RANDOM_STATE = 42
N_FOLDS = 5

NUMERIC_FEATURES = [
    "statement_length",
    "operator_count",
    "operand_count",
    "expression_depth",
    "loop_depth",
    "condition_count",
    "logical_operator_count",
    "enclosing_loop_depth",
]

# Record types written by generate_dataset.py. The labels depend on the
# record type (only loop headers can be nested loops, only if/while tests
# can be complex conditionals, only simple statements can be long), and
# loop_depth also counts loops inside an if's body, so the type is needed
# to tell a nested for-loop header from an if that contains one.
STATEMENT_TYPES = [
    "Assign",
    "AnnAssign",
    "AugAssign",
    "Expr",
    "Return",
    "If",
    "For",
    "AsyncFor",
    "While",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + [f"type_{t}" for t in STATEMENT_TYPES]

LABEL_COLUMNS = [
    "long_statement",
    "nested_loop",
    "complex_conditional",
]


def load_dataset(dataset_path=DATASET_PATH):
    # "None" is a real intended_category value, not a missing value.
    return pd.read_csv(dataset_path, keep_default_na=False)


def build_features(data):
    """Feature matrix in FEATURE_COLUMNS order for any dataset rows."""
    unknown = set(data["statement_type"]) - set(STATEMENT_TYPES)
    if unknown:
        raise ValueError(f"Unknown statement types: {sorted(unknown)}")
    features = data[NUMERIC_FEATURES].astype(float).copy()
    for statement_type in STATEMENT_TYPES:
        is_type = data["statement_type"] == statement_type
        features[f"type_{statement_type}"] = is_type.astype(float)
    return features[FEATURE_COLUMNS]


def new_model():
    forest = RandomForestClassifier(
        n_estimators=200,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    return MultiOutputClassifier(forest)


def program_split(data, fold=0):
    """
    Row masks (train, test) for one fold of a group split.

    Groups are similarity groups, so near-duplicate programs stay on one
    side. Stratifying on intended_category keeps all eight categories in
    the test programs. Fold 0 holds out about 1 / N_FOLDS of the programs.
    """
    programs = data.drop_duplicates("program_id")
    splitter = StratifiedGroupKFold(
        n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )
    folds = list(splitter.split(
        programs, programs["intended_category"], programs["similarity_group"]
    ))
    test_programs = set(programs.iloc[folds[fold][1]]["program_id"])
    test = data["program_id"].isin(test_programs).to_numpy()
    return ~test, test


def label_metrics(y_true, y_pred):
    """Per-label precision, recall, F1 and confusion counts."""
    metrics = {}
    for i, label in enumerate(LABEL_COLUMNS):
        truth, pred = y_true[:, i], y_pred[:, i]
        tn, fp, fn, tp = confusion_matrix(truth, pred, labels=[0, 1]).ravel()
        metrics[label] = {
            "precision": round(precision_score(truth, pred, zero_division=0), 4),
            "recall": round(recall_score(truth, pred, zero_division=0), 4),
            "f1": round(f1_score(truth, pred, zero_division=0), 4),
            "support": int(truth.sum()),
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        }
    return metrics


def overall_metrics(y_true, y_pred):
    return {
        "exact_match_accuracy": round(accuracy_score(y_true, y_pred), 4),
        "hamming_loss": round(hamming_loss(y_true, y_pred), 4),
        "macro_f1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "micro_f1": round(f1_score(y_true, y_pred, average="micro", zero_division=0), 4),
    }


def fit_and_score(data, train, test):
    model = new_model()
    model.fit(build_features(data[train]), data.loc[train, LABEL_COLUMNS])
    y_true = data.loc[test, LABEL_COLUMNS].to_numpy()
    y_pred = model.predict(build_features(data[test]))
    return model, y_true, y_pred


def cross_validate(data):
    """Macro and per-label F1 over all N_FOLDS grouped folds."""
    per_fold = []
    for fold in range(N_FOLDS):
        train, test = program_split(data, fold)
        _, y_true, y_pred = fit_and_score(data, train, test)
        scores = {
            label: f1_score(y_true[:, i], y_pred[:, i], zero_division=0)
            for i, label in enumerate(LABEL_COLUMNS)
        }
        scores["macro_f1"] = f1_score(y_true, y_pred, average="macro", zero_division=0)
        per_fold.append(scores)
    summary = {}
    for key in per_fold[0]:
        values = np.array([fold[key] for fold in per_fold])
        summary[key] = {"mean": round(values.mean(), 4), "std": round(values.std(), 4)}
    return summary


def cross_model_check(data):
    """Train on programs from one generating LLM and test on the other."""
    results = {}
    models = sorted(data["model_name"].unique())
    for held_out in models:
        test = (data["model_name"] == held_out).to_numpy()
        _, y_true, y_pred = fit_and_score(data, ~test, test)
        results[f"test_on_{held_out}"] = {
            "test_rows": int(test.sum()),
            **overall_metrics(y_true, y_pred),
            "per_label_f1": {
                label: round(f1_score(y_true[:, i], y_pred[:, i], zero_division=0), 4)
                for i, label in enumerate(LABEL_COLUMNS)
            },
        }
    return results


def train_model(dataset_path=DATASET_PATH):
    """Train on the training programs; return (model, data, train, test)."""
    data = load_dataset(dataset_path)
    train, test = program_split(data)
    model = new_model()
    model.fit(build_features(data[train]), data.loc[train, LABEL_COLUMNS])
    return model, data, train, test


def feature_importance(model):
    importances = np.mean(
        [estimator.feature_importances_ for estimator in model.estimators_], axis=0
    )
    return (
        pd.DataFrame({"feature": FEATURE_COLUMNS, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def main():
    model, data, train, test = train_model()
    test_rows = data[test]
    y_true = test_rows[LABEL_COLUMNS].to_numpy()
    y_pred = model.predict(build_features(test_rows))

    train_groups = set(data.loc[train, "similarity_group"])
    test_groups = set(data.loc[test, "similarity_group"])
    if train_groups & test_groups:
        raise RuntimeError("A similarity group is on both sides of the split.")

    evaluation = {
        "dataset": {
            "rows": len(data),
            "programs": int(data["program_id"].nunique()),
            "similarity_groups": int(data["similarity_group"].nunique()),
        },
        "split": {
            "method": f"StratifiedGroupKFold fold 0 of {N_FOLDS} "
                      "(groups = similarity_group, strata = intended_category)",
            "train_programs": int(data.loc[train, "program_id"].nunique()),
            "test_programs": int(test_rows["program_id"].nunique()),
            "train_rows": int(train.sum()),
            "test_rows": int(test.sum()),
            "test_programs_per_category": (
                test_rows.drop_duplicates("program_id")["intended_category"]
                .value_counts().sort_index().to_dict()
            ),
        },
        "features": FEATURE_COLUMNS,
        "labels": LABEL_COLUMNS,
        "test_set": {
            **overall_metrics(y_true, y_pred),
            "per_label": label_metrics(y_true, y_pred),
        },
        "grouped_cross_validation": cross_validate(data),
        "cross_model": cross_model_check(data),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    (RESULTS_DIR / "model_evaluation.json").write_text(
        json.dumps(evaluation, indent=2), encoding="utf-8"
    )
    predictions = test_rows[[
        "program_id", "statement_id", "line_no", "end_line",
        "statement_type", "in_main_guard", "code", *LABEL_COLUMNS,
    ]].copy()
    for i, label in enumerate(LABEL_COLUMNS):
        predictions[f"pred_{label}"] = y_pred[:, i]
    predictions.to_csv(RESULTS_DIR / "test_predictions.csv", index=False)
    importance = feature_importance(model)
    importance.to_csv(RESULTS_DIR / "feature_importance.csv", index=False)

    split = evaluation["split"]
    print("Model training completed.")
    print(f"Train: {split['train_programs']} programs, {split['train_rows']} rows | "
          f"Test: {split['test_programs']} programs, {split['test_rows']} rows")
    print("\nHeld-out test programs:")
    for label, m in evaluation["test_set"]["per_label"].items():
        print(f"  {label:20s} P={m['precision']:.3f} R={m['recall']:.3f} "
              f"F1={m['f1']:.3f}  (TP={m['tp']} FP={m['fp']} FN={m['fn']})")
    for key in ("exact_match_accuracy", "hamming_loss", "macro_f1"):
        print(f"  {key}: {evaluation['test_set'][key]}")
    print(f"\nGrouped {N_FOLDS}-fold cross-validation (F1 mean +/- std):")
    for key, value in evaluation["grouped_cross_validation"].items():
        print(f"  {key:20s} {value['mean']:.3f} +/- {value['std']:.3f}")
    print("\nCross-model check (train on the other LLM's programs):")
    for key, value in evaluation["cross_model"].items():
        print(f"  {key}: macro F1 {value['macro_f1']}, per label {value['per_label_f1']}")
    print("\nTop features:")
    for _, row in importance.head(6).iterrows():
        print(f"  {row['feature']:24s} {row['importance']:.3f}")
    print(f"\nSaved model to {MODEL_PATH.relative_to(BASE_DIR)} and results to "
          f"{RESULTS_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    main()
