"""
transformation.py
Stage 8 of the pipeline: transformation engine.

Applies the automatable recommendations from stage 7 to the program
source. Edits are made on the source lines, so comments and formatting
outside the rewritten statements are kept. Edits are applied from the
bottom of the file up and the file is re-parsed after each one, so every
edit sees the current code; an edit that does not parse is undone.

Refactorings (each keeps evaluation order and short-circuiting):
- DECOMPOSE_EXPRESSION: a long arithmetic Assign/AnnAssign/AugAssign/Return
  value is built up left to right in a variable, one short step per line:
      total = a * b + c * d
      total = total + e * f
- DECOMPOSE_BOOLEAN: the same for a long and/or chain (Assign/AnnAssign/
  Return), e.g. ok = a and b / ok = ok and c.
- EXTRACT_CONDITION: an if/elif test is built up in a named variable
  just before the test. An elif becomes else: + if, so its condition is
  still only evaluated when the earlier branches fail.
- FLATTEN_WITH_PRODUCT: perfectly nested for-loops over independent,
  side-effect-free iterables become one loop over itertools.product.

applicability() gives the reason an action cannot be applied to a
statement ("" if it can); stage 7 uses it to mark recommendations as
automatable.

Outputs (written to results/):
  refactored_programs/P####.py  transformed held-out programs
  transformation_summary.json   applied / skipped counts and reasons
"""

import ast
import io
import json
import tokenize
from collections import Counter
from pathlib import Path

from generate_dataset import header_colon_position, statement_length

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
REFACTORED_DIR = RESULTS_DIR / "refactored_programs"

LINE_LIMIT = 60
LOOP_TYPES = (ast.For, ast.AsyncFor, ast.While)
SCOPES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
CHAINABLE_VALUE_TYPES = {
    "DECOMPOSE_EXPRESSION": (ast.BinOp, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Return)),
    "DECOMPOSE_BOOLEAN": (ast.BoolOp, (ast.Assign, ast.AnnAssign, ast.Return)),
}
SAFE_ITERABLE_CALLS = {
    "range", "len", "enumerate", "zip", "reversed", "sorted", "list", "tuple",
    "min", "max", "abs",
}
SAFE_OPERATORS = (ast.Add, ast.Sub, ast.Mult)


class NotApplicable(Exception):
    pass


# ---------------------------------------------------------------- helpers

def parents_of(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def enclosing_scope(node, parents):
    while not isinstance(node, SCOPES):
        node = parents[node]
    return node


def identifiers(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names.update(node.names)
    return names


def names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


class NameMaker:
    """New variable names that clash with nothing in the module."""

    def __init__(self, tree):
        self.original = identifiers(tree)
        self.taken = set(self.original)
        self.created = {}

    def new(self, base):
        name, number = base, 2
        while name in self.taken:
            name, number = f"{base}_{number}", number + 1
        self.taken.add(name)
        self.created[name] = base
        return name

    def renumber(self, source):
        """
        Rename the created names so each base is numbered in order of
        first appearance (condition, condition_2, ...). Edits run bottom-up,
        so the names were handed out in reverse.
        """
        positions = {}
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        for token in tokens:
            if token.type == tokenize.NAME and token.string in self.created:
                positions.setdefault(token.string, token.start)

        mapping, taken = {}, set(self.original)
        for name in sorted(positions, key=positions.get):
            base = self.created[name]
            new, number = base, 2
            while new in taken:
                new, number = f"{base}_{number}", number + 1
            taken.add(new)
            mapping[name] = new
        if all(old == new for old, new in mapping.items()):
            return source

        lines = source.splitlines(keepends=True)
        for token in reversed(tokens):
            if token.type == tokenize.NAME and token.string in mapping:
                row, col = token.start
                line = lines[row - 1]
                lines[row - 1] = line[:col] + mapping[token.string] + line[token.end[1]:]
        return "".join(lines)


def fits(text):
    return statement_length(text) <= LINE_LIMIT


def code(expr):
    """
    Source for expr. and/or chains are written out here because
    ast.unparse puts needless brackets around their third and later
    operands.
    """
    if not isinstance(expr, ast.BoolOp):
        return ast.unparse(expr)
    joiner = " and " if isinstance(expr.op, ast.And) else " or "
    parts = []
    for value in expr.values:
        text = code(value)
        if isinstance(value, (ast.BoolOp, ast.IfExp, ast.Lambda, ast.NamedExpr)):
            text = f"({text})"
        parts.append(text)
    return joiner.join(parts)


def indentation(line):
    return line[:len(line) - len(line.lstrip())]


def has_multiline_string(node):
    return any(
        isinstance(n, (ast.Constant, ast.JoinedStr))
        and (isinstance(n, ast.JoinedStr) or isinstance(n.value, (str, bytes)))
        and n.end_lineno > n.lineno
        for n in ast.walk(node)
    )


def find_statement(tree, line_no, statement_type):
    for node in ast.walk(tree):
        if type(node).__name__ == statement_type and getattr(node, "lineno", None) == line_no:
            return node
    raise LookupError(f"no {statement_type} at line {line_no}")


# ------------------------------------------------- building up a chain

def chain_terms(expr):
    """(first, [(op, operand), ...]) so that folding left gives expr back."""
    if isinstance(expr, ast.BoolOp):
        return expr.values[0], [(expr.op, value) for value in expr.values[1:]]
    steps = []
    while isinstance(expr, ast.BinOp):
        steps.insert(0, (expr.op, expr.right))
        expr = expr.left
    return expr, steps


def combine(acc, op, operand):
    if isinstance(op, ast.boolop):
        values = acc.values if isinstance(acc, ast.BoolOp) and type(acc.op) is type(op) else [acc]
        return ast.BoolOp(op=op, values=[*values, operand])
    return ast.BinOp(left=acc, op=op, right=operand)


def is_name(expr, name):
    return isinstance(expr, ast.Name) and expr.id == name


def build_boolean(name, expr, unit):
    """
    Lines that leave the value of an and/or chain in name.

    Operands are packed into groups that fit LINE_LIMIT; every group after
    the first is computed under `if name:` (and) or `if not name:` (or),
    so it is only evaluated when the original short-circuit would
    evaluate it, and name ends with exactly the original value.
    """
    def line(value):
        return f"{name} = {code(value)}"

    groups = []
    for value in expr.values:
        if groups and fits(line(ast.BoolOp(op=expr.op, values=groups[-1] + [value]))):
            groups[-1].append(value)
        else:
            groups.append([value])

    guard = "if not" if isinstance(expr.op, ast.Or) else "if"
    lines = []
    for index, group in enumerate(groups):
        value = group[0] if len(group) == 1 else ast.BoolOp(op=expr.op, values=group)
        if isinstance(value, ast.BoolOp) and len(group) == 1 and not fits(line(value)):
            body = build_boolean(name, value, unit)
        else:
            body = [line(value)]
        if index:
            lines.append(f"{guard} {name}:")
            body = [unit + text for text in body]
        lines += body
    return lines


def build_arithmetic(name, expr, used, unit):
    """
    Lines that compute a prefix of an arithmetic chain into name, and the
    expression (in terms of name) that completes it. Operands are added
    left to right; a long operand that is itself arithmetic is computed
    into its own variable just before it is used.
    """
    def line(value):
        return f"{name} = {code(value)}"

    stored = ast.Name(id=name, ctx=ast.Load())
    acc, steps = chain_terms(expr)
    lines = []
    for op, operand in steps:
        candidate = combine(acc, op, operand)
        if fits(line(candidate)):
            acc = candidate
            continue
        if acc is not stored:
            lines.append(line(acc))
            acc = stored
            candidate = combine(stored, op, operand)
            if fits(line(candidate)) or not isinstance(operand, ast.BinOp):
                acc = candidate
                continue
        part = used.new("part")
        sub, rest = build_arithmetic(part, operand, used, unit)
        lines += sub
        if not is_name(rest, part):
            lines.append(f"{part} = {code(rest)}")
        acc = combine(stored, op, ast.Name(id=part, ctx=ast.Load()))
    return lines, acc


def build_up(name, expr, used, unit):
    """
    Lines (indented relative to the statement by multiples of unit) that
    compute part of expr into name, and the expression that completes it.
    Each line fits LINE_LIMIT unless a single operand is already too long.
    """
    if isinstance(expr, ast.BoolOp):
        return build_boolean(name, expr, unit), ast.Name(id=name, ctx=ast.Load())
    return build_arithmetic(name, expr, used, unit)


# ------------------------------------------------------- applicability

def decompose_reason(action, node, parents):
    value_type, statement_types = CHAINABLE_VALUE_TYPES[action]
    if not isinstance(node, statement_types):
        return f"{action} is not implemented for {type(node).__name__} statements"
    if not isinstance(node.value, value_type):
        return f"value is a {type(node.value).__name__}, not a {value_type.__name__} chain"
    if isinstance(enclosing_scope(node, parents), ast.ClassDef):
        return "statement is in a class body"
    if isinstance(node, ast.AnnAssign) and not isinstance(node.target, ast.Name):
        return "annotated target is not a plain name"
    return ""


def is_safe_iterable(expr):
    """Expressions that cannot raise or have side effects when evaluated early."""
    if isinstance(expr, (ast.Name, ast.Constant)):
        return True
    if isinstance(expr, (ast.Tuple, ast.List)):
        return all(is_safe_iterable(e) for e in expr.elts)
    if isinstance(expr, ast.UnaryOp):
        return is_safe_iterable(expr.operand)
    if isinstance(expr, ast.BinOp):
        return (isinstance(expr.op, SAFE_OPERATORS)
                and is_safe_iterable(expr.left) and is_safe_iterable(expr.right))
    if isinstance(expr, ast.Call):
        return (isinstance(expr.func, ast.Name) and expr.func.id in SAFE_ITERABLE_CALLS
                and not expr.keywords and all(is_safe_iterable(a) for a in expr.args))
    return False


def mutates(body_nodes, names):
    """True if the statements may rebind or mutate any of names."""
    for stmt in body_nodes:
        for n in ast.walk(stmt):
            if isinstance(n, ast.Name) and n.id in names and not isinstance(n.ctx, ast.Load):
                return True
            if (isinstance(n, (ast.Attribute, ast.Subscript))
                    and isinstance(n.value, ast.Name) and n.value.id in names):
                if isinstance(n, ast.Attribute) or not isinstance(n.ctx, ast.Load):
                    return True
    return False


def breaks_out_of(loop):
    """True if a break in loop's body (outside nested loops) exits loop."""
    def visit(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Break):
                return True
            if isinstance(child, LOOP_TYPES) or isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            if visit(child):
                return True
        return False
    return any(visit(stmt) or isinstance(stmt, ast.Break) for stmt in loop.body)


def loaded_outside(names, loop, scope):
    """Names read in scope outside loop, other than by another binding of them."""
    def visit(node):
        if node is loop:
            return False
        if isinstance(node, (ast.For, ast.AsyncFor)) and names & names_in(node.target):
            return False
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            if names & {n for g in node.generators for n in names_in(g.target)}:
                return False
        if isinstance(node, ast.Name) and node.id in names and isinstance(node.ctx, ast.Load):
            return True
        if node is not scope and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return False
        return any(visit(child) for child in ast.iter_child_nodes(node))
    return visit(scope)


def product_levels(loop, parents):
    """The perfectly nested for-loops that can be merged into one product loop."""
    levels = [loop]
    targets = names_in(loop.target)
    current = loop
    while (
        isinstance(current, ast.For) and not current.orelse
        and len(current.body) == 1 and isinstance(current.body[0], ast.For)
    ):
        inner = current.body[0]
        iter_names = names_in(inner.iter)
        if (
            inner.orelse
            or targets & iter_names
            or not is_safe_iterable(inner.iter)
            or mutates(inner.body, iter_names | names_in(loop.iter))
            or breaks_out_of(inner)
            or has_multiline_string(inner)
        ):
            break
        levels.append(inner)
        targets |= names_in(inner.target)
        current = inner
    if len(levels) > 1:
        scope = enclosing_scope(loop, parents)
        if loaded_outside(targets, loop, scope):
            return [loop]
    return levels


def flatten_reason(node, parents):
    if not isinstance(node, ast.For):
        return f"FLATTEN_WITH_PRODUCT is not implemented for {type(node).__name__} loops"
    if len(product_levels(node, parents)) < 2:
        return ("inner loop is not perfectly nested, depends on the outer loop, "
                "breaks, or its iterable is not side-effect free")
    return ""


def condition_reason(node, source_lines, parents):
    if not isinstance(node, ast.If):
        return f"EXTRACT_CONDITION is not implemented for {type(node).__name__} statements"
    if is_elif(node, source_lines, parents) and has_multiline_string(parents[node]):
        return "elif chain contains a multi-line string, which re-indenting would change"
    return ""


def applicability(action, node, tree, source_lines, parents=None):
    """Reason the action cannot be applied to node, or "" if it can."""
    parents = parents or parents_of(tree)
    if action in CHAINABLE_VALUE_TYPES:
        return decompose_reason(action, node, parents)
    if action == "EXTRACT_CONDITION":
        return condition_reason(node, source_lines, parents)
    if action == "FLATTEN_WITH_PRODUCT":
        reason = flatten_reason(node, parents)
        if not reason and product_name(tree) is None and itertools_shadowed(tree):
            reason = "the name itertools is already used for something else"
        return reason
    return f"transformation.py does not implement {action} yet"


# ------------------------------------------------------------ edits

def is_elif(node, source_lines, parents):
    parent = parents.get(node)
    return (
        isinstance(parent, ast.If) and parent.orelse == [node]
        and source_lines[node.lineno - 1].lstrip().startswith("elif")
    )


def indent_unit_of(tree, source_lines):
    """The file's indentation step, taken from its first indented block."""
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, ast.stmt) and isinstance(body, list) and body:
            unit = indent_unit(source_lines, node, body)
            if unit:
                return unit
    return "    "


def indent_unit(source_lines, header, body):
    return indentation(source_lines[body[0].lineno - 1])[len(indentation(source_lines[header.lineno - 1])):]


def decompose(node, source_lines, used, unit):
    indent = indentation(source_lines[node.lineno - 1])
    value = node.value
    referenced = names_in(value)

    if isinstance(node, ast.Return):
        name = used.new("result")
        lines, rest = build_up(name, value, used, unit)
        final = f"return {code(rest)}"
    elif isinstance(node, ast.AugAssign):
        target = ast.unparse(node.target)
        name = used.new("change")
        lines, rest = build_up(name, value, used, unit)
        op = ast.unparse(ast.AugAssign(target=ast.Name("x"), op=node.op, value=ast.Name("y")))
        final = f"{target} {op.split()[1]} {code(rest)}"
    else:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        single = len(targets) == 1 and isinstance(targets[0], ast.Name)
        # Arithmetic steps repeat the name (x = x + ...), so it must be short.
        short_enough = isinstance(value, ast.BoolOp) or len(targets[0].id if single else "") <= 12
        if single and targets[0].id not in referenced and short_enough:
            name = targets[0].id
        elif isinstance(value, ast.BinOp):
            name = used.new("partial")
        else:
            name = used.new("value")
        lines, rest = build_up(name, value, used, unit)
        target_text = " = ".join(ast.unparse(t) for t in targets)
        final = f"{target_text} = {code(rest)}"
        if isinstance(rest, ast.Name) and rest.id == name and target_text == name:
            final = None
        if isinstance(node, ast.AnnAssign):
            annotation = ast.unparse(node.annotation)
            if lines and name == target_text:
                lines[0] = lines[0].replace(f"{name} = ", f"{name}: {annotation} = ", 1)
            elif final:
                final = final.replace(f"{target_text} = ", f"{target_text}: {annotation} = ", 1)

    if not lines:
        raise NotApplicable("the expression could not be split into shorter steps")
    new = lines + ([final] if final else [])
    return node.lineno, node.end_lineno, [indent + text + "\n" for text in new]


def extract_condition(node, source_lines, parents, used):
    colon_line, _ = header_colon_position(node, source_lines)
    indent = indentation(source_lines[node.lineno - 1])
    unit = indent_unit(source_lines, node, node.body)
    name = used.new("condition")
    lines, rest = build_up(name, node.test, used, unit)
    if not is_name(rest, name):
        lines.append(f"{name} = {code(rest)}")

    if not is_elif(node, source_lines, parents):
        new = [indent + text + "\n" for text in lines] + [f"{indent}if {name}:\n"]
        return node.lineno, colon_line, new

    inner = indent + unit
    new = [f"{indent}else:\n"]
    new += [inner + text + "\n" for text in lines] + [f"{inner}if {name}:\n"]
    for line in source_lines[colon_line:node.end_lineno]:
        new.append(unit + line if line.strip() else line)
    return node.lineno, node.end_lineno, new


def itertools_shadowed(tree):
    """True if the module binds the name itertools to something else."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "itertools" and not isinstance(node.ctx, ast.Load):
            return True
        if isinstance(node, ast.arg) and node.arg == "itertools":
            return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == "itertools":
            return True
        if isinstance(node, ast.alias) and (node.asname or node.name) == "itertools" and node.name != "itertools":
            return True
    return False


def product_name(tree):
    for node in tree.body:
        if isinstance(node, ast.Import) and any(a.name == "itertools" and not a.asname for a in node.names):
            return "itertools.product"
        if isinstance(node, ast.ImportFrom) and node.module == "itertools":
            if any(a.name == "product" and not a.asname for a in node.names):
                return "product"
    return None


def flatten(node, source_lines, parents, tree):
    levels = product_levels(node, parents)
    innermost = levels[-1]
    colon_line, _ = header_colon_position(innermost, source_lines)
    indent = indentation(source_lines[node.lineno - 1])
    extra = (
        len(indentation(source_lines[innermost.body[0].lineno - 1]))
        - len(indentation(source_lines[node.body[0].lineno - 1]))
    )
    targets = ", ".join(ast.unparse(level.target) for level in levels)
    iterables = ", ".join(ast.unparse(level.iter) for level in levels)
    product = product_name(tree) or "itertools.product"
    new = [f"{indent}for {targets} in {product}({iterables}):\n"]
    for line in source_lines[colon_line:innermost.end_lineno]:
        strip = min(extra, len(indentation(line)))
        new.append(line[strip:] if line.strip() else line)
    return node.lineno, innermost.end_lineno, new


def add_itertools_import(source):
    tree = ast.parse(source)
    if product_name(tree):
        return source
    lines = source.splitlines(keepends=True)
    position = 0
    for node in tree.body:
        is_docstring = (
            node is tree.body[0] and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        )
        if is_docstring or (isinstance(node, ast.ImportFrom) and node.module == "__future__"):
            position = node.end_lineno
            continue
        break
    follows = lines[position] if position < len(lines) else ""
    insert = ["import itertools\n"]
    if position:
        insert.insert(0, "\n")
    if follows.strip() and not follows.startswith(("import ", "from ")):
        insert.append("\n")
    return "".join(lines[:position] + insert + lines[position:])


def apply_one(source, target, used):
    """Apply one action to source and return the new source."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    parents = parents_of(tree)
    node = find_statement(tree, target["line_no"], target["statement_type"])
    reason = applicability(target["action"], node, tree, lines, parents)
    if reason:
        raise NotApplicable(reason)

    action = target["action"]
    if action in CHAINABLE_VALUE_TYPES:
        start, end, new = decompose(node, lines, used, indent_unit_of(tree, lines))
    elif action == "EXTRACT_CONDITION":
        start, end, new = extract_condition(node, lines, parents, used)
    else:
        start, end, new = flatten(node, lines, parents, tree)

    result = "".join(lines[:start - 1] + new + lines[end:])
    ast.parse(result)
    return result


def transform_source(source, targets):
    """
    Apply automatable actions to source.

    targets: dicts with line_no, statement_type and action (line numbers
    refer to source). Returns (new_source, outcomes), one outcome per
    target with status "applied", "covered" (merged into another edit) or
    "skipped" with a reason.
    """
    tree = ast.parse(source)
    parents = parents_of(tree)
    lines = source.splitlines(keepends=True)
    used = NameMaker(tree)

    covered_by = {}
    for target in targets:
        if target["action"] != "FLATTEN_WITH_PRODUCT":
            continue
        node = find_statement(tree, target["line_no"], target["statement_type"])
        if not applicability(target["action"], node, tree, lines, parents):
            for level in product_levels(node, parents)[1:]:
                covered_by.setdefault(level.lineno, target["line_no"])

    outcomes = []
    ordered = sorted(targets, key=lambda t: t["line_no"], reverse=True)
    for target in ordered:
        outcome = {key: target[key] for key in ("line_no", "statement_type", "action")}
        if target["action"] == "FLATTEN_WITH_PRODUCT" and target["line_no"] in covered_by:
            outcome.update(status="covered",
                           detail=f"merged into the loop at line {covered_by[target['line_no']]}")
            outcomes.append(outcome)
            continue
        try:
            source = apply_one(source, target, used)
            outcome.update(status="applied", detail="")
        except (NotApplicable, LookupError, SyntaxError) as error:
            outcome.update(status="skipped", detail=str(error))
        outcomes.append(outcome)

    source = used.renumber(source)
    # Added last: it shifts every line below it.
    if any(o["action"] == "FLATTEN_WITH_PRODUCT" and o["status"] == "applied"
           for o in outcomes):
        source = add_itertools_import(source)
    outcomes.sort(key=lambda o: o["line_no"])
    return source, outcomes


def long_statement_count(source):
    """Simple statements in source still over LINE_LIMIT."""
    from generate_dataset import extract_statements
    records = extract_statements(ast.parse(source), source.splitlines(keepends=True))
    return sum(r["long_statement"] for r in records if not r["in_main_guard"])


# --------------------------------------------------------------- stage 8

def automatable_targets(result):
    return [
        {"line_no": result["line_no"], "statement_type": result["statement_type"],
         "action": r["action"]}
        for r in result["recommendations"] if r["automatable"]
    ]


def transform_programs(recommendation_results, source_for):
    """Transform every program with automatable recommendations."""
    by_program = {}
    for result in recommendation_results:
        by_program.setdefault((result["program_id"], result["filename"]), []).append(result)

    programs = {}
    for (pid, filename), results in sorted(by_program.items()):
        targets = [t for result in results for t in automatable_targets(result)]
        if not targets:
            continue
        original = source_for(results[0])
        transformed, outcomes = transform_source(original, targets)
        programs[pid] = {
            "filename": filename,
            "original": original,
            "transformed": transformed,
            "outcomes": outcomes,
        }
    return programs


def summarize(programs):
    outcomes = [o for p in programs.values() for o in p["outcomes"]]
    by_action = {}
    for action in sorted({o["action"] for o in outcomes}):
        of_action = [o for o in outcomes if o["action"] == action]
        by_action[action] = dict(Counter(o["status"] for o in of_action))
    reasons = Counter(o["detail"] for o in outcomes if o["status"] == "skipped")
    return {
        "programs_transformed": sum(p["original"] != p["transformed"] for p in programs.values()),
        "targets": len(outcomes),
        "status": dict(Counter(o["status"] for o in outcomes)),
        "by_action": by_action,
        "skip_reasons": dict(reasons.most_common()),
        "long_statements_before": sum(long_statement_count(p["original"]) for p in programs.values()),
        "long_statements_after": sum(long_statement_count(p["transformed"]) for p in programs.values()),
    }


def main():
    from localization import localize_test_programs, program_source
    from recommendation import recommend_refactorings
    from train_model import train_model

    model, data, _, test = train_model()
    issues, _, _ = localize_test_programs(model, data, test)
    results = recommend_refactorings(issues)
    programs = transform_programs(results, program_source)
    summary = summarize(programs)

    REFACTORED_DIR.mkdir(parents=True, exist_ok=True)
    for old in REFACTORED_DIR.glob("*.py"):
        old.unlink()
    for program in programs.values():
        (REFACTORED_DIR / program["filename"]).write_text(program["transformed"], encoding="utf-8")
    (RESULTS_DIR / "transformation_summary.json").write_text(
        json.dumps({
            **summary,
            "outcomes": {pid: p["outcomes"] for pid, p in programs.items()},
        }, indent=2),
        encoding="utf-8",
    )

    print(f"Programs transformed: {summary['programs_transformed']}")
    print(f"Automatable targets: {summary['targets']} -> {summary['status']}")
    for action, counts in summary["by_action"].items():
        print(f"  {action:24s} {counts}")
    if summary["skip_reasons"]:
        print("Skipped because:")
        for reason, count in summary["skip_reasons"].items():
            print(f"  {count:3d}  {reason}")
    print(f"Long statements (outside __main__) in these programs: "
          f"{summary['long_statements_before']} before, {summary['long_statements_after']} after")
    print(f"\nSaved refactored programs to {REFACTORED_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    main()
