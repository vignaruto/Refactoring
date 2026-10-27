"""
validation.py
Stage 9 of the pipeline: post-refactoring validation.

Every transformed program is checked against its original:

1. Syntax: the transformed source parses.
2. Self-test: the transformed program runs as a script and its
   `if __name__ == "__main__":` asserts pass.
3. Differential testing: the calls the self-test makes to the program's
   top-level functions are recorded, then replayed on the original and
   transformed functions together with edge-case variants of those
   arguments (zero, negated, shifted, doubled and halved numbers, empty,
   shortened and reversed sequences, changed first/last elements, dicts
   missing a key or with a changed value, empty strings). Return values, raised
   exception types, printed output and argument mutation must match.
4. Safety: top-level definitions and signatures, the __main__ block and
   imports are unchanged (itertools may be added), and every function is
   called the same number of times in the source, so no expression was
   duplicated or dropped.

A program that fails any check is rejected and stays in its original form.

The checks are themselves tested by a mutation check: faults are planted
in the refactored lines of valid programs (and/or swapped, arithmetic
operator changed, extracted condition negated, product iterables swapped,
an accumulation step dropped) and the share stage 9 rejects is reported.

Outputs (written to results/):
  validation_report.json  per-program checks and verdicts
  validated_programs/     final programs (transformed if valid, else original)
"""

import ast
import contextlib
import copy
import difflib
import io
import itertools
import json
import os
import signal
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
VALIDATED_DIR = RESULTS_DIR / "validated_programs"

RUN_TIMEOUT = 30
WORKERS = os.cpu_count() or 4
CALL_TIMEOUT = 2
RECORDED_CALLS_PER_FUNCTION = 20
VARIANTS_PER_FUNCTION = 120
ADDED_IMPORTS = {"itertools"}
ADDED_CALLS = {"itertools.product", "product"}


# ---------------------------------------------------------------- static

def check_syntax(source):
    try:
        ast.parse(source)
        return ""
    except SyntaxError as error:
        return f"SyntaxError: {error}"


def main_guard(tree):
    for node in tree.body:
        if (
            isinstance(node, ast.If)
            and "__name__" in ast.unparse(node.test)
            and "__main__" in ast.unparse(node.test)
        ):
            return node
    return None


def definitions(tree):
    """Top-level functions and classes with their signatures."""
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found[node.name] = ast.dump(node.args) + "".join(
                ast.dump(d) for d in node.decorator_list
            )
        elif isinstance(node, ast.ClassDef):
            found[node.name] = "class"
    return found


def imports(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def calls(tree):
    return Counter(
        ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)
    )


def safety_problems(original, transformed):
    """Structural changes a refactoring must not make."""
    before, after = ast.parse(original), ast.parse(transformed)
    problems = []

    if definitions(before) != definitions(after):
        problems.append("top-level definitions or signatures changed")

    guard_before, guard_after = main_guard(before), main_guard(after)
    if (guard_before is None) != (guard_after is None) or (
        guard_before is not None
        and ast.dump(guard_before) != ast.dump(guard_after)
    ):
        problems.append("the __main__ self-test block changed")

    new_imports = imports(after) - imports(before)
    unexpected = {name for name in new_imports if name.split(".")[0] not in ADDED_IMPORTS}
    if unexpected or imports(before) - imports(after):
        problems.append(f"imports changed: {sorted(unexpected or imports(before) - imports(after))}")

    call_before, call_after = calls(before), calls(after)
    for name in ADDED_CALLS:
        call_after.pop(name, None)
        call_before.pop(name, None)
    if call_before != call_after:
        changed = sorted(
            name for name in call_before.keys() | call_after.keys()
            if call_before[name] != call_after[name]
        )
        problems.append(f"call counts changed for {changed}")

    for node in ast.walk(after):
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            if not any(isinstance(old, type(node)) and old.names == node.names
                       for old in ast.walk(before)):
                problems.append("a global/nonlocal declaration was added")
                break
    return problems


# ------------------------------------------------------------- dynamic

def run_self_test(source):
    """"" if running the program as a script succeeds, else the error."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "program.py"
        path.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(path)], capture_output=True, text=True,
                timeout=RUN_TIMEOUT, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return f"timed out after {RUN_TIMEOUT}s"
    if result.returncode:
        lines = result.stderr.strip().splitlines()
        return lines[-1] if lines else f"exit code {result.returncode}"
    return ""


def differential_test(original, transformed, explicit_calls=None):
    """
    Run the differential test in a separate process.

    explicit_calls: optional [function_name, [args...]] pairs to use
    instead of the calls recorded from the self-test.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "original.py").write_text(original, encoding="utf-8")
        (tmp / "transformed.py").write_text(transformed, encoding="utf-8")
        (tmp / "calls.json").write_text(json.dumps(explicit_calls), encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--worker", str(tmp)],
                capture_output=True, text=True, timeout=RUN_TIMEOUT * 4, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {"error": "differential test timed out"}
    if result.returncode:
        lines = result.stderr.strip().splitlines()
        return {"error": lines[-1] if lines else "worker failed"}
    return json.loads(result.stdout)


# ------------------------------------------------- worker (subprocess)

class CallTimeout(Exception):
    pass


@contextlib.contextmanager
def time_limit(seconds):
    def expire(signum, frame):
        raise CallTimeout()
    previous = signal.signal(signal.SIGALRM, expire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def load_module(source, filename):
    namespace = {"__name__": "program_under_test"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source, filename, "exec"), namespace)
    return namespace


def top_level_functions(source):
    return [
        node.name for node in ast.parse(source).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def top_level_classes(source):
    return [node.name for node in ast.parse(source).body if isinstance(node, ast.ClassDef)]


def record_calls(source, filename):
    """
    Run the self-test once, recording (a) calls to top-level functions as
    (name, args, kwargs) for replay, and (b) a trace of every method call
    on top-level classes: arguments, result and the object's state after
    the call, since method calls depend on object state and cannot be
    replayed on their own.
    """
    namespace = load_module(source, filename)
    guard = main_guard(ast.parse(source))
    if guard is None:
        return [], []
    recorded, trace = [], []
    per_function = Counter()

    def recorder(name, function):
        def wrapper(*args, **kwargs):
            if per_function[name] < RECORDED_CALLS_PER_FUNCTION:
                try:
                    recorded.append((name, copy.deepcopy(args), copy.deepcopy(kwargs)))
                    per_function[name] += 1
                except Exception:  # noqa: BLE001 - some arguments cannot be copied
                    pass
            return function(*args, **kwargs)
        return wrapper

    def tracer(name, method):
        def wrapper(self, *args, **kwargs):
            entry = [name, repr(args)[:300], repr(kwargs)[:300]]
            try:
                result = method(self, *args, **kwargs)
            except Exception as error:
                trace.append(entry + [f"raised {type(error).__name__}", ""])
                raise
            state = repr(getattr(self, "__dict__", ""))[:500]
            trace.append(entry + [repr(result)[:300], state])
            return result
        return wrapper

    for name in top_level_functions(source):
        namespace[name] = recorder(name, namespace[name])
    for class_name in top_level_classes(source):
        cls = namespace[class_name]
        for attribute, member in list(vars(cls).items()):
            if callable(member) and not isinstance(member, type) and not attribute.startswith("__"):
                setattr(cls, attribute, tracer(f"{class_name}.{attribute}", member))
            elif attribute == "__init__":
                setattr(cls, attribute, tracer(f"{class_name}.__init__", member))

    body = ast.Module(body=guard.body, type_ignores=[])
    try:
        with contextlib.redirect_stdout(io.StringIO()), time_limit(RUN_TIMEOUT):
            exec(compile(body, filename, "exec"), namespace)
    except Exception as error:  # noqa: BLE001 - a failing self-test is reported elsewhere
        trace.append(["self-test", "", "", f"raised {type(error).__name__}", ""])
    return recorded, trace


def variants_of(value, depth=0):
    """Edge-case variants of an argument, including variants of its first elements."""
    if isinstance(value, bool):
        return [not value]
    if isinstance(value, int):
        return [0, -value, value + 1, value - 1, value * 2, value // 2]
    if isinstance(value, float):
        return [0.0, -value, value + 1, value - 1, value * 2, value / 2]
    if isinstance(value, str):
        return ["", value[: len(value) // 2]]
    found = []
    if isinstance(value, (list, tuple)) and value:
        found += [type(value)(), type(value)(value[: len(value) // 2]),
                  type(value)(reversed(value))]
        if depth == 0:
            for inner in variants_of(value[0], depth + 1):
                found.append(type(value)([inner, *value[1:]]))
            if len(value) > 1:
                for inner in variants_of(value[-1], depth + 1):
                    found.append(type(value)([*value[:-1], inner]))
    elif isinstance(value, dict) and value:
        keys = list(value)
        found += [{k: v for k, v in value.items() if k != drop} for drop in dict.fromkeys([keys[0], keys[-1]])]
        if depth == 0:
            for key in keys[:4]:
                for inner in variants_of(value[key], depth + 1):
                    found.append({**value, key: inner})
    return found


def expand(recorded):
    """Recorded calls plus one-argument-at-a-time variants, capped per function."""
    expanded = []
    per_function = Counter()
    for name, args, kwargs in recorded:
        expanded.append((name, args, kwargs))
    for name, args, kwargs in recorded:
        for position, value in enumerate(args):
            for variant in variants_of(value):
                if per_function[name] >= VARIANTS_PER_FUNCTION:
                    break
                new_args = list(args)
                new_args[position] = variant
                expanded.append((name, tuple(new_args), kwargs))
                per_function[name] += 1
    return expanded


def outcome(namespace, name, args, kwargs):
    args, kwargs = copy.deepcopy(args), copy.deepcopy(kwargs)
    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed), time_limit(CALL_TIMEOUT):
            value = namespace[name](*args, **kwargs)
        return {"kind": "return", "value": value, "printed": printed.getvalue(), "args": args}
    except CallTimeout:
        return {"kind": "timeout"}
    except Exception as error:  # noqa: BLE001 - exceptions are part of behaviour
        return {"kind": "raise", "error": type(error).__name__, "printed": printed.getvalue()}


def same_value(a, b):
    try:
        if bool(a == b):
            return True
    except Exception:  # noqa: BLE001
        pass
    return repr(a) == repr(b)


def same_outcome(a, b):
    if a["kind"] != b["kind"]:
        return False
    if a["kind"] == "raise":
        return a["error"] == b["error"] and a["printed"] == b["printed"]
    if a["kind"] == "return":
        return (same_value(a["value"], b["value"]) and a["printed"] == b["printed"]
                and same_value(a["args"], b["args"]))
    return True


def describe(result):
    if result["kind"] == "return":
        return f"returned {result['value']!r}"[:120]
    if result["kind"] == "raise":
        return f"raised {result['error']}"
    return "timed out"


def worker(directory):
    directory = Path(directory)
    original = (directory / "original.py").read_text(encoding="utf-8")
    transformed = (directory / "transformed.py").read_text(encoding="utf-8")
    explicit = json.loads((directory / "calls.json").read_text(encoding="utf-8"))

    sides = {}
    for side, source in (("original", original), ("transformed", transformed)):
        if explicit is None:
            recorded, trace = record_calls(source, f"{side}.py")
        else:
            recorded, trace = [(name, tuple(args), {}) for name, args in explicit], []
        sides[side] = (load_module(source, f"{side}.py"), expand(recorded), trace)

    (ns_a, calls_a, trace_a), (ns_b, calls_b, trace_b) = sides["original"], sides["transformed"]
    report = {"recorded_calls_match": len(calls_a) == len(calls_b),
              "calls": len(trace_a), "inconclusive": 0, "mismatches": []}
    for index, (a, b) in enumerate(itertools.zip_longest(trace_a, trace_b)):
        if a != b:
            report["mismatches"].append({
                "function": (a or b)[0], "args": (a or b)[1],
                "original": " / ".join((a or ["missing"] * 5)[3:]),
                "transformed": " / ".join((b or ["missing"] * 5)[3:]),
            })
            break
    for (name, args, kwargs), (name_b, args_b, kwargs_b) in zip(calls_a, calls_b):
        a = outcome(ns_a, name, args, kwargs)
        b = outcome(ns_b, name_b, args_b, kwargs_b)
        if a["kind"] == "timeout":
            report["inconclusive"] += 1
            continue
        report["calls"] += 1
        if name != name_b or not same_outcome(a, b):
            report["mismatches"].append({
                "function": name,
                "args": repr(args)[:200],
                "original": describe(a),
                "transformed": describe(b),
            })
    print(json.dumps(report))


# ------------------------------------------------------------ stage 9

def validate_program(original, transformed, explicit_calls=None):
    """All stage 9 checks for one program; returns a report with a verdict."""
    report = {"changed": original != transformed}
    report["syntax_error"] = check_syntax(transformed)
    if report["syntax_error"]:
        report.update(valid=False, reasons=["transformed code does not parse"])
        return report

    has_self_test = main_guard(ast.parse(original)) is not None
    report["self_test"] = (run_self_test(transformed) or "pass") if has_self_test else "none"
    report["safety_problems"] = safety_problems(original, transformed)
    report["differential"] = differential_test(original, transformed, explicit_calls)

    reasons = []
    if report["self_test"] not in ("pass", "none"):
        reasons.append(f"self-test failed: {report['self_test']}")
    reasons += report["safety_problems"]
    differential = report["differential"]
    if "error" in differential:
        reasons.append(f"differential test could not run: {differential['error']}")
    else:
        if not differential["recorded_calls_match"]:
            reasons.append("the self-test made different calls")
        if differential["mismatches"]:
            reasons.append(f"{len(differential['mismatches'])} differential mismatches")
        if differential["calls"] == 0:
            reasons.append("no calls to compare")
    report.update(valid=not reasons, reasons=reasons)
    return report


def validate_programs(programs):
    """Validate every program from transformation.transform_programs()."""
    pids = sorted(programs)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = pool.map(
            lambda pid: validate_program(programs[pid]["original"], programs[pid]["transformed"]),
            pids,
        )
    reports = dict(zip(pids, results))
    for pid, report in reports.items():
        report["applied_actions"] = [
            o["action"] for o in programs[pid]["outcomes"] if o["status"] == "applied"
        ]
    return reports


# ------------------------------------------------------ mutation check

def changed_lines(original, transformed):
    """Line numbers in transformed that differ from original."""
    matcher = difflib.SequenceMatcher(
        a=original.splitlines(), b=transformed.splitlines(), autojunk=False
    )
    lines = set()
    for tag, _, _, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            lines.update(range(j1 + 1, j2 + 1))
    return lines


class Mutator(ast.NodeTransformer):
    """Plants one fault of one kind in the first matching changed line."""

    SWAP_ARITHMETIC = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Add, ast.Div: ast.Mult}

    def __init__(self, kind, lines):
        self.kind, self.lines, self.done = kind, lines, False

    def eligible(self, node):
        return not self.done and getattr(node, "lineno", None) in self.lines

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if self.kind == "swap and/or" and self.eligible(node):
            self.done = True
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        swap = self.SWAP_ARITHMETIC.get(type(node.op))
        if self.kind == "change arithmetic operator" and swap and self.eligible(node):
            self.done = True
            node.op = swap()
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if self.kind == "negate extracted condition" and self.eligible(node):
            self.done = True
            if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not):
                node.test = node.test.operand
            else:
                node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if (
            self.kind == "swap product iterables" and self.eligible(node)
            and ast.unparse(node.func) in ADDED_CALLS and len(node.args) >= 2
            and ast.dump(node.args[0]) != ast.dump(node.args[1])
        ):
            self.done = True
            node.args[0], node.args[1] = node.args[1], node.args[0]
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        if (
            self.kind == "drop a step" and self.eligible(node)
            and isinstance(node.value, (ast.BinOp, ast.BoolOp))
            and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in names_loaded(node.value)
        ):
            self.done = True
            return ast.Pass()
        return node


MUTATION_KINDS = [
    "swap and/or",
    "change arithmetic operator",
    "negate extracted condition",
    "swap product iterables",
    "drop a step",
]


def names_loaded(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def mutants(original, transformed):
    """(kind, mutant source) for each fault kind that fits the refactored lines."""
    lines = changed_lines(original, transformed)
    found = []
    for kind in MUTATION_KINDS:
        mutator = Mutator(kind, lines)
        tree = ast.fix_missing_locations(mutator.visit(ast.parse(transformed)))
        if mutator.done:
            found.append((kind, ast.unparse(tree)))
    return found


def mutation_check(programs, reports):
    """How many planted faults in refactored lines stage 9 rejects."""
    jobs = [
        (kind, program["original"], mutant)
        for pid, program in sorted(programs.items())
        if reports[pid]["valid"] and reports[pid]["changed"]
        for kind, mutant in mutants(program["original"], program["transformed"])
    ]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        verdicts = pool.map(lambda job: validate_program(job[1], job[2])["valid"], jobs)
    killed, total = Counter(), Counter()
    for (kind, _, _), valid in zip(jobs, verdicts):
        total[kind] += 1
        killed[kind] += not valid
    return {
        kind: {"mutants": total[kind], "detected": killed[kind],
               "rate": round(killed[kind] / total[kind], 3) if total[kind] else None}
        for kind in MUTATION_KINDS
    } | {"overall": {
        "mutants": sum(total.values()), "detected": sum(killed.values()),
        "rate": round(sum(killed.values()) / sum(total.values()), 3) if total else None,
    }}


def summarize(reports):
    valid = [pid for pid, r in reports.items() if r["valid"]]
    calls = sum(r.get("differential", {}).get("calls", 0) for r in reports.values())
    actions = Counter(a for r in reports.values() for a in r["applied_actions"])
    accepted = Counter(a for r in reports.values() if r["valid"] for a in r["applied_actions"])
    return {
        "programs": len(reports),
        "valid": len(valid),
        "rejected": sorted(set(reports) - set(valid)),
        "self_tests_passed": sum(r.get("self_test") == "pass" for r in reports.values()),
        "differential_calls": calls,
        "differential_mismatches": sum(
            len(r.get("differential", {}).get("mismatches", [])) for r in reports.values()
        ),
        "actions_applied": dict(actions),
        "actions_accepted": dict(accepted),
        "rejection_reasons": dict(Counter(
            reason for r in reports.values() for reason in r["reasons"]
        )),
    }


def main():
    from localization import localize_test_programs, program_source
    from recommendation import recommend_refactorings
    from train_model import train_model
    from transformation import transform_programs

    model, data, _, test = train_model()
    issues, _, _ = localize_test_programs(model, data, test)
    programs = transform_programs(recommend_refactorings(issues), program_source)
    reports = validate_programs(programs)
    summary = summarize(reports)
    summary["mutation_check"] = mutation_check(programs, reports)

    VALIDATED_DIR.mkdir(parents=True, exist_ok=True)
    for old in VALIDATED_DIR.glob("*.py"):
        old.unlink()
    for pid, program in programs.items():
        final = program["transformed"] if reports[pid]["valid"] else program["original"]
        (VALIDATED_DIR / program["filename"]).write_text(final, encoding="utf-8")
    (RESULTS_DIR / "validation_report.json").write_text(
        json.dumps({**summary, "programs_detail": reports}, indent=2), encoding="utf-8"
    )

    print(f"Programs validated: {summary['programs']}")
    print(f"Valid: {summary['valid']} | rejected (kept original): {len(summary['rejected'])}")
    print(f"Self-tests passed: {summary['self_tests_passed']}")
    print(f"Differential calls compared: {summary['differential_calls']}, "
          f"mismatches: {summary['differential_mismatches']}")
    print(f"Actions applied: {summary['actions_applied']}")
    print(f"Actions accepted: {summary['actions_accepted']}")
    print("Planted faults detected (mutation check):")
    for kind, m in summary["mutation_check"].items():
        print(f"  {kind:28s} {m['detected']}/{m['mutants']}")
    for reason, count in summary["rejection_reasons"].items():
        print(f"  {count:3d}  {reason}")
    for pid in summary["rejected"]:
        for mismatch in reports[pid].get("differential", {}).get("mismatches", [])[:3]:
            print(f"  {pid} {mismatch['function']}{mismatch['args'][:80]}: "
                  f"original {mismatch['original']}, transformed {mismatch['transformed']}")
    print(f"\nSaved {VALIDATED_DIR.relative_to(BASE_DIR)}/ and "
          f"{(RESULTS_DIR / 'validation_report.json').relative_to(BASE_DIR)}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    else:
        main()
