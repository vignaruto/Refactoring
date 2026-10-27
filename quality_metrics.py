"""
quality_metrics.py
Stage 10 of the pipeline: before-and-after evaluation.

Compares every held-out program before refactoring with its final,
validated form from stage 9 (programs that were not changed or were
rejected count as unchanged).

1. Pipeline funnel: issues detected -> automatable -> applied ->
   accepted by validation -> resolved.
2. Target issues, outside the __main__ self-test block: per issue type
   how many were resolved and how many new ones the refactoring
   introduced, by the labelling rules and by re-running the trained
   detector on the refactored code.
3. Independent quality metrics (not the rules the issues are defined
   by): cyclomatic and cognitive complexity, maintainability index,
   Halstead volume and difficulty, logical lines, nesting depth,
   statement length and conditions per test. For each, before/after
   means and medians, how many programs got better or worse, and a
   paired Wilcoxon signed-rank test over the changed programs, and the
   mean change in programs where only one kind of refactoring was applied.

Outputs (written to results/):
  quality_metrics.csv      per-program metric values before and after
  quality_evaluation.json  funnel, issue resolution and metric statistics
"""

import ast
import json
from collections import Counter
from pathlib import Path

import pandas as pd
from cognitive_complexity.api import get_cognitive_complexity
from radon.complexity import cc_visit
from radon.metrics import h_visit, mi_visit
from radon.raw import analyze
from scipy.stats import wilcoxon

from generate_dataset import count_atomic_conditions, extract_statements

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

ISSUES = ["long_statement", "nested_loop", "complex_conditional"]
COMPOUND = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)

# metric -> (description, True if higher is better)
METRICS = {
    "cyclomatic_complexity": ("sum of McCabe complexity over functions (radon)", False),
    "max_cyclomatic_complexity": ("highest McCabe complexity of one function", False),
    "cognitive_complexity": ("sum of cognitive complexity over functions", False),
    "max_cognitive_complexity": ("highest cognitive complexity of one function", False),
    "maintainability_index": ("radon maintainability index, 0-100", True),
    "halstead_volume": ("Halstead volume (radon)", False),
    "halstead_difficulty": ("Halstead difficulty (radon)", False),
    "logical_lines": ("logical lines of code (radon lloc)", False),
    "max_nesting_depth": ("deepest nesting of compound statements in a function", False),
    "max_statement_length": ("longest simple statement, measured on one line", False),
    "mean_statement_length": ("mean simple-statement length", False),
    "max_condition_atoms": ("most atomic conditions in one if/while test", False),
    "long_statements": ("long statements (rule)", False),
    "nested_loops": ("nested loop headers (rule)", False),
    "complex_conditionals": ("complex conditionals (rule)", False),
}


# ------------------------------------------------------------ metrics

def program_code(source):
    """source without its __main__ self-test block."""
    tree = ast.parse(source)
    for node in tree.body:
        if (isinstance(node, ast.If) and "__name__" in ast.unparse(node.test)
                and "__main__" in ast.unparse(node.test)):
            lines = source.splitlines(keepends=True)
            return "".join(lines[:node.lineno - 1] + lines[node.end_lineno:])
    return source


def records_outside_main(source):
    records = extract_statements(ast.parse(source), source.splitlines(keepends=True))
    return [r for r in records if not r["in_main_guard"]]


def nesting_depth(node, depth=0):
    deepest = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, FUNCTIONS + (ast.ClassDef,)):
            continue
        inner = depth + 1 if isinstance(child, COMPOUND) else depth
        deepest = max(deepest, nesting_depth(child, inner))
    return deepest


def functions_of(tree):
    """Top-level functions and methods of top-level classes."""
    found = []
    for node in tree.body:
        if isinstance(node, FUNCTIONS):
            found.append(node)
        elif isinstance(node, ast.ClassDef):
            found += [n for n in node.body if isinstance(n, FUNCTIONS)]
    return found


def calculate_metrics(source):
    code = program_code(source)
    tree = ast.parse(code)
    functions = functions_of(tree)
    records = records_outside_main(source)
    simple = [r["statement_length"] for r in records
              if r["statement_type"] in {"Assign", "AnnAssign", "AugAssign", "Expr", "Return"}]
    conditions = [count_atomic_conditions(n.test) for n in ast.walk(tree)
                  if isinstance(n, (ast.If, ast.While))]
    cyclomatic = [block.complexity for block in cc_visit(code)
                  if type(block).__name__ == "Function"]
    cognitive = [get_cognitive_complexity(f) for f in functions]
    halstead = h_visit(code).total
    return {
        "cyclomatic_complexity": sum(cyclomatic),
        "max_cyclomatic_complexity": max(cyclomatic, default=0),
        "cognitive_complexity": sum(cognitive),
        "max_cognitive_complexity": max(cognitive, default=0),
        "maintainability_index": round(mi_visit(code, multi=True), 2),
        "halstead_volume": round(halstead.volume, 2),
        "halstead_difficulty": round(halstead.difficulty, 2),
        "logical_lines": analyze(code).lloc,
        "max_nesting_depth": max((nesting_depth(f) for f in functions), default=0),
        "max_statement_length": max(simple, default=0),
        "mean_statement_length": round(sum(simple) / len(simple), 2) if simple else 0,
        "max_condition_atoms": max(conditions, default=0),
        "long_statements": sum(r["long_statement"] for r in records),
        "nested_loops": sum(r["nested_loop"] for r in records),
        "complex_conditionals": sum(r["complex_conditional"] for r in records),
    }


# ------------------------------------------------------ issue changes

def issue_changes(before, after):
    """Per issue type: issues before/after, resolved and newly introduced."""
    flagged_before = records_outside_main(before)
    flagged_after = records_outside_main(after)
    changes = {}
    for label in ISSUES:
        old = Counter(r["code"] for r in flagged_before if r[label])
        new = Counter(r["code"] for r in flagged_after if r[label])
        kept = sum((old & new).values())
        changes[label] = {
            "before": sum(old.values()),
            "after": sum(new.values()),
            "resolved": sum(old.values()) - kept,
            "introduced": sum(new.values()) - kept,
        }
    return changes


def detected_counts(model, source):
    from localization import localize_source

    issues, _ = localize_source(model, source)
    return Counter(
        label for issue in issues if not issue["in_main_guard"]
        for label in issue["detected_issues"]
    )


# --------------------------------------------------------- statistics

def metric_statistics(table):
    """Before/after summary and a paired Wilcoxon test for each metric."""
    stats = {}
    changed = table[table["changed"]]
    for metric, (description, higher_is_better) in METRICS.items():
        before, after = table[f"{metric}_before"], table[f"{metric}_after"]
        delta = after - before
        better = (delta > 0) if higher_is_better else (delta < 0)
        worse = (delta < 0) if higher_is_better else (delta > 0)
        changed_delta = changed[f"{metric}_after"] - changed[f"{metric}_before"]
        try:
            p_value = float(wilcoxon(changed_delta, zero_method="zsplit").pvalue)
        except ValueError:
            p_value = None
        stats[metric] = {
            "description": description,
            "higher_is_better": higher_is_better,
            "mean_before": round(float(before.mean()), 3),
            "mean_after": round(float(after.mean()), 3),
            "median_before": float(before.median()),
            "median_after": float(after.median()),
            "mean_change": round(float(delta.mean()), 3),
            "programs_better": int(better.sum()),
            "programs_worse": int(worse.sum()),
            "programs_same": int((delta == 0).sum()),
            "wilcoxon_p_changed_programs": None if p_value is None else round(p_value, 6),
        }
    return stats


# ------------------------------------------------------------ stage 10

def evaluate(model, programs_before, programs_after, changed):
    """
    programs_before / programs_after: {pid: source}; changed: pids whose
    final source differs. Returns (table, issue resolution totals).
    """
    rows = []
    totals = {label: Counter() for label in ISSUES}
    detected = {"before": Counter(), "after": Counter()}
    for pid in sorted(programs_before):
        before, after = programs_before[pid], programs_after[pid]
        row = {"program_id": pid, "changed": pid in changed}
        for side, source in (("before", before), ("after", after)):
            for metric, value in calculate_metrics(source).items():
                row[f"{metric}_{side}"] = value
        for label, counts in issue_changes(before, after).items():
            totals[label].update(counts)
        if model is not None:
            detected["before"].update(detected_counts(model, before))
            detected["after"].update(
                detected_counts(model, after) if pid in changed
                else detected_counts(model, before)
            )
        rows.append(row)
    resolution = {
        label: {
            **dict(totals[label]),
            "resolution_rate": round(totals[label]["resolved"] / totals[label]["before"], 3)
            if totals[label]["before"] else None,
            "detected_by_model_before": detected["before"][label],
            "detected_by_model_after": detected["after"][label],
        }
        for label in ISSUES
    }
    return pd.DataFrame(rows), resolution


def single_action_effects(table, transformations, changed):
    """Mean metric change in programs where only one kind of action was applied."""
    kinds = {
        pid: {o["action"] for o in transformations[pid]["outcomes"] if o["status"] == "applied"}
        for pid in changed
    }
    effects = {}
    for action in sorted({a for actions in kinds.values() for a in actions}):
        pids = [pid for pid, actions in kinds.items() if actions == {action}]
        rows = table[table["program_id"].isin(pids)]
        effects[action] = {"programs": len(pids)} | {
            metric: round(float((rows[f"{metric}_after"] - rows[f"{metric}_before"]).mean()), 3)
            for metric in METRICS
        } if pids else {"programs": 0}
    return effects


def funnel(issues, recommendations, transformations, reports):
    recs = [r for result in recommendations for r in result["recommendations"]]
    outcomes = [o for p in transformations.values() for o in p["outcomes"]]
    applied = Counter(o["action"] for o in outcomes if o["status"] == "applied")
    accepted = sum(
        o["status"] == "applied" for pid, p in transformations.items()
        if reports[pid]["valid"] for o in p["outcomes"]
    )
    return {
        "issues_detected": sum(len(i["detected_issues"]) for i in issues),
        "in_main_guard_left_unchanged": sum(
            r["reason"].startswith("in the __main__") for r in recs
        ),
        "automatable": sum(r["automatable"] for r in recs),
        "applied": sum(applied.values()),
        "merged_into_another_edit": sum(o["status"] == "covered" for o in outcomes),
        "skipped_by_transformer": sum(o["status"] == "skipped" for o in outcomes),
        "accepted_by_validation": accepted,
        "programs_changed": sum(
            reports[pid]["valid"] and reports[pid]["changed"] for pid in transformations
        ),
    }


def compare_metrics(original_code, transformed_code):
    """Print a before/after metric table for one program."""
    before = calculate_metrics(original_code)
    after = calculate_metrics(transformed_code)
    print("\n========== QUALITY METRICS ==========")
    print(f"{'Metric':<28} {'Before':>10} {'After':>10}  Change")
    print("-" * 60)
    for metric, (_, higher_is_better) in METRICS.items():
        delta = after[metric] - before[metric]
        verdict = "same" if delta == 0 else (
            "better" if (delta > 0) == higher_is_better else "worse"
        )
        print(f"{metric:<28} {before[metric]:>10} {after[metric]:>10}  {verdict}")
    print("\n========== TARGET ISSUES ==========")
    for label, counts in issue_changes(original_code, transformed_code).items():
        print(f"{label:<20} before {counts['before']}, after {counts['after']} "
              f"(resolved {counts['resolved']}, introduced {counts['introduced']})")
    return before, after


def main():
    from localization import localize_test_programs, program_source
    from recommendation import recommend_refactorings
    from train_model import train_model
    from transformation import transform_programs
    from validation import validate_programs

    model, data, _, test = train_model()
    issues, _, _ = localize_test_programs(model, data, test)
    recommendations = recommend_refactorings(issues)
    transformations = transform_programs(recommendations, program_source)
    reports = validate_programs(transformations)

    test_programs = data[test].drop_duplicates("program_id")
    before = {
        row.program_id: program_source({"filename": row.filename})
        for row in test_programs.itertuples()
    }
    after = dict(before)
    changed = set()
    for pid, program in transformations.items():
        if reports[pid]["valid"] and reports[pid]["changed"]:
            after[pid] = program["transformed"]
            changed.add(pid)

    table, resolution = evaluate(model, before, after, changed)
    stats = metric_statistics(table)
    evaluation = {
        "programs": len(table),
        "programs_changed": len(changed),
        "funnel": funnel(issues, recommendations, transformations, reports),
        "issue_resolution": resolution,
        "metrics": stats,
        "single_action_effects": single_action_effects(table, transformations, changed),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    table.to_csv(RESULTS_DIR / "quality_metrics.csv", index=False)
    (RESULTS_DIR / "quality_evaluation.json").write_text(
        json.dumps(evaluation, indent=2), encoding="utf-8"
    )

    print(f"Held-out programs: {len(table)} ({len(changed)} changed by validated refactorings)")
    print("\nPipeline funnel:")
    for step, count in evaluation["funnel"].items():
        print(f"  {step:32s} {count}")
    print("\nTarget issues outside __main__ (rules; model re-detection in brackets):")
    for label, r in resolution.items():
        print(f"  {label:20s} {r['before']:4d} -> {r['after']:4d}  resolved {r['resolved']:3d} "
              f"({r['resolution_rate']:.0%}), introduced {r['introduced']:3d}  "
              f"[model {r['detected_by_model_before']} -> {r['detected_by_model_after']}]")
    print("\nQuality metrics (mean over all held-out programs; Wilcoxon p over changed ones):")
    print(f"  {'metric':28s} {'before':>8} {'after':>8} {'better':>7} {'worse':>6}  p")
    for metric, s in stats.items():
        p = "-" if s["wilcoxon_p_changed_programs"] is None else f"{s['wilcoxon_p_changed_programs']:.2g}"
        print(f"  {metric:28s} {s['mean_before']:8.2f} {s['mean_after']:8.2f} "
              f"{s['programs_better']:7d} {s['programs_worse']:6d}  {p}")
    shown = ["cognitive_complexity", "maintainability_index", "logical_lines",
             "halstead_difficulty", "max_nesting_depth", "max_statement_length"]
    print("\nMean change in programs with only one kind of refactoring:")
    print(f"  {'action':24s} {'n':>3} " + " ".join(f"{m[:12]:>12}" for m in shown))
    for action, effect in evaluation["single_action_effects"].items():
        if effect["programs"]:
            print(f"  {action:24s} {effect['programs']:3d} "
                  + " ".join(f"{effect[m]:12.2f}" for m in shown))
    print(f"\nSaved results to {RESULTS_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    main()
