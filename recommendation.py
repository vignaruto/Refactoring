"""
recommendation.py
Stage 7 of the pipeline: recommendation engine.

For every localized issue, looks at the statement's syntax tree in its
source file and recommends a refactoring that fits its shape, e.g. a long
arithmetic assignment is split into named partial results while a long
call gets its arguments extracted. Each recommendation records:

- the refactoring and its action code;
- the pattern it was chosen for and how far the statement is over the
  issue's threshold (severity);
- whether transformation.py can apply it automatically, and if not, why.

Issues inside the `if __name__ == "__main__":` test block are reported but
not recommended for change, since that block is the program's self-test.

Outputs (written to results/):
  recommendations.json        recommendations per held-out program
  recommendation_summary.json counts per refactoring and automation coverage
"""

import ast
import json
from collections import Counter
from pathlib import Path

from generate_dataset import (
    calculate_subtree_loop_depth,
    count_atomic_conditions,
    statement_length,
)
from localization import program_source
from transformation import SUPPORTED_ACTIONS

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

LONG_STATEMENT_LIMIT = 60
CONDITION_ATOM_LIMIT = 3
NESTING_LIMIT = 1

LITERALS = (ast.List, ast.Tuple, ast.Set, ast.Dict)
COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)

REFACTORINGS = {
    "DECOMPOSE_EXPRESSION": (
        "Decompose Expression",
        "Split the arithmetic into named partial results.",
    ),
    "DECOMPOSE_BOOLEAN": (
        "Decompose Boolean Expression",
        "Give the sub-conditions names and combine the names.",
    ),
    "EXTRACT_ARGUMENTS": (
        "Extract Arguments",
        "Compute the long arguments into named variables before the call.",
    ),
    "EXTRACT_ELEMENTS": (
        "Extract Elements",
        "Compute the long elements into named variables, then build the literal.",
    ),
    "REPLACE_CONDITIONAL_EXPRESSION": (
        "Replace Conditional Expression",
        "Use an if/else statement instead of the inline conditional.",
    ),
    "SIMPLIFY_COMPREHENSION": (
        "Simplify Comprehension",
        "Move the element expression or filter into a named helper.",
    ),
    "INTRODUCE_EXPLAINING_VARIABLE": (
        "Introduce Explaining Variable",
        "Name a sub-expression to shorten the statement.",
    ),
    "EXTRACT_CONDITION": (
        "Extract Condition",
        "Name the condition (or its parts) before the if/elif.",
    ),
    "EXTRACT_PREDICATE": (
        "Extract Predicate Function",
        "Move the loop condition into a helper function, since a while test "
        "is re-evaluated on every iteration.",
    ),
    "FLATTEN_WITH_PRODUCT": (
        "Flatten Nested Loop",
        "Replace the perfectly nested loops with one loop over itertools.product.",
    ),
    "EXTRACT_INNER_LOOP": (
        "Extract Inner Loop",
        "Move the inner loop into a helper function.",
    ),
}


def find_statement(tree, issue):
    """The statement node a localized issue refers to."""
    for node in ast.walk(tree):
        if (
            type(node).__name__ == issue["statement_type"]
            and getattr(node, "lineno", None) == issue["line_no"]
        ):
            return node
    raise LookupError(
        f"{issue['program_id'] or issue['filename']}: no "
        f"{issue['statement_type']} at line {issue['line_no']}"
    )


def names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def long_statement_action(node):
    value = node.value
    if isinstance(value, ast.BinOp):
        return "DECOMPOSE_EXPRESSION", "arithmetic expression"
    if isinstance(value, (ast.BoolOp, ast.Compare)) or (
        isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not)
    ):
        return "DECOMPOSE_BOOLEAN", "boolean expression"
    if isinstance(value, ast.Call):
        return "EXTRACT_ARGUMENTS", "function call"
    if isinstance(value, LITERALS):
        return "EXTRACT_ELEMENTS", f"{type(value).__name__.lower()} literal"
    if isinstance(value, ast.IfExp):
        return "REPLACE_CONDITIONAL_EXPRESSION", "conditional expression"
    if isinstance(value, COMPREHENSIONS):
        return "SIMPLIFY_COMPREHENSION", "comprehension"
    return "INTRODUCE_EXPLAINING_VARIABLE", type(value).__name__


def can_flatten_with_product(node):
    """
    True for `for a in X: for b in Y: body` where Y does not use a and
    nothing changes the iteration (no break/continue/else), so the pair
    of loops visits exactly the pairs in itertools.product(X, Y).
    """
    if not isinstance(node, ast.For) or node.orelse or len(node.body) != 1:
        return False
    inner = node.body[0]
    if not isinstance(inner, ast.For) or inner.orelse:
        return False
    if names_in(node.target) & names_in(inner.iter):
        return False
    return not any(
        isinstance(n, (ast.Break, ast.Continue)) for n in ast.walk(inner)
    )


def nested_loop_action(node):
    if can_flatten_with_product(node):
        return "FLATTEN_WITH_PRODUCT", "perfectly nested independent for-loops"
    if isinstance(node, ast.While):
        return "EXTRACT_INNER_LOOP", "while loop containing a loop"
    return "EXTRACT_INNER_LOOP", "loop with a dependent or non-perfect inner loop"


def complex_conditional_action(node):
    if isinstance(node, ast.While):
        return "EXTRACT_PREDICATE", "while condition"
    return "EXTRACT_CONDITION", "if/elif condition"


def severity(label, issue, node):
    """(measure, value, smallest flagged value) using the dataset's own measurements."""
    if label == "long_statement":
        return "statement_length", statement_length(issue["code"]), LONG_STATEMENT_LIMIT + 1
    if label == "complex_conditional":
        return "atomic_conditions", count_atomic_conditions(node.test), CONDITION_ATOM_LIMIT
    return "loop_depth", calculate_subtree_loop_depth(node), NESTING_LIMIT + 1


ACTION_CHOOSERS = {
    "long_statement": long_statement_action,
    "nested_loop": nested_loop_action,
    "complex_conditional": complex_conditional_action,
}


def recommend(issue, label, node):
    action, pattern = ACTION_CHOOSERS[label](node)
    name, description = REFACTORINGS[action]
    measure, value, threshold = severity(label, issue, node)

    if issue["in_main_guard"]:
        automatable, reason = False, "in the __main__ self-test block; leave unchanged"
    elif (action, issue["statement_type"]) in SUPPORTED_ACTIONS:
        automatable, reason = True, ""
    else:
        automatable, reason = False, (
            f"transformation.py does not implement {action} "
            f"for {issue['statement_type']} statements yet"
        )

    return {
        "issue": label,
        "refactoring": name,
        "action": action,
        "description": description,
        "pattern": pattern,
        "severity": {"measure": measure, "value": value, "flagged_at": threshold},
        "confidence": issue.get("confidence", {}).get(label),
        "automatable": automatable,
        "reason": reason,
    }


def recommend_refactorings(localized_issues, source_for=program_source):
    """Attach recommendations to each localized issue."""
    trees = {}
    results = []
    for issue in localized_issues:
        key = issue["program_id"] or issue["filename"]
        if key not in trees:
            trees[key] = ast.parse(source_for(issue))
        node = find_statement(trees[key], issue)
        results.append({
            **issue,
            "recommendations": [
                recommend(issue, label, node) for label in issue["detected_issues"]
            ],
        })
    return results


def summarize(results):
    recommendations = [r for result in results for r in result["recommendations"]]
    by_action = Counter(r["action"] for r in recommendations)
    automatable = Counter(r["action"] for r in recommendations if r["automatable"])
    summary = {
        "statements": len(results),
        "recommendations": len(recommendations),
        "automatable": sum(automatable.values()),
        "in_main_guard": sum(
            r["reason"].startswith("in the __main__") for r in recommendations
        ),
        "by_issue": {},
        "by_action": {
            action: {"count": count, "automatable": automatable[action]}
            for action, count in by_action.most_common()
        },
    }
    for label in ACTION_CHOOSERS:
        of_label = [r for r in recommendations if r["issue"] == label]
        summary["by_issue"][label] = {
            "count": len(of_label),
            "automatable": sum(r["automatable"] for r in of_label),
            "actions": dict(Counter(r["action"] for r in of_label).most_common()),
        }
    return summary


def main():
    from localization import group_by_program, localize_test_programs
    from train_model import train_model

    model, data, _, test = train_model()
    issues, _, _ = localize_test_programs(model, data, test)
    results = recommend_refactorings(issues)
    summary = summarize(results)

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "recommendations.json").write_text(
        json.dumps(group_by_program(results), indent=2), encoding="utf-8"
    )
    (RESULTS_DIR / "recommendation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print(f"Recommendations: {summary['recommendations']} for "
          f"{summary['statements']} statements in the held-out programs")
    print(f"Automatable now: {summary['automatable']} | "
          f"in __main__ test block (left unchanged): {summary['in_main_guard']}")
    print("\nBy issue:")
    for label, s in summary["by_issue"].items():
        print(f"  {label:20s} {s['count']:4d} issues, {s['automatable']:4d} automatable")
        for action, count in s["actions"].items():
            print(f"      {action:32s} {count}")
    print(f"\nSaved results to {RESULTS_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    main()
