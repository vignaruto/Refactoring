import ast
import csv
import re
import html
from pathlib import Path

from validate_corpus import similarity_groups


# =========================================================
# S7 PROJECT: CORPUS-WIDE DATASET GENERATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

CORPUS_DIR = BASE_DIR / "program_corpus" / "programs"
MANIFEST_FILE = BASE_DIR / "program_corpus" / "manifest.csv"
OUTPUT_FILE = BASE_DIR / "dataset.csv"

LONG_STATEMENT_THRESHOLD = 60
COMPLEX_CONDITION_THRESHOLD = 3

SIMPLE_STATEMENTS = (
    ast.Assign,
    ast.AnnAssign,
    ast.AugAssign,
    ast.Expr,
    ast.Return,
)

LOOP_STATEMENTS = (
    ast.For,
    ast.AsyncFor,
    ast.While,
)

HEADER_STATEMENTS = (ast.If,) + LOOP_STATEMENTS

SCOPE_STATEMENTS = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
)


# =========================================================
# STATEMENT-RECORD POLICY
# =========================================================
#
# A dataset record is one of:
#   - a simple statement: Assign, AnnAssign, AugAssign, Expr, Return;
#   - the header of a compound statement: If (each elif is its own If
#     record), For, AsyncFor, While.
#
# A header record covers the source from the keyword up to and
# including its colon, e.g. "for row in matrix:". Body statements are
# separate records, so no source text belongs to two records.
#
# Records come from walking statement lists in source order: module,
# class and function bodies, and the body / else / except / finally /
# case blocks of compound statements. Other statements (def, class,
# with, try, match, import, ...) are not records, but their blocks are
# still walked.
#
# Module, class and function docstrings (a string literal that is the
# first statement of that body) are documentation and are not records.
# Any other standalone string expression is an ordinary Expr record.
#
# Feature scope:
#   - code, statement_length, operator_count, operand_count,
#     expression_depth, condition_count and logical_operator_count are
#     computed only from the construct the record represents: the whole
#     simple statement, the if/while test, or the for target and
#     iterable. Trailing comments are not part of a record.
#   - statement_length (and so long_statement) counts a multi-line
#     record as if written on one line: each line break and the
#     indentation around it become one space, or nothing next to an
#     opening or closing bracket. The code column keeps the original.
#   - in_main_guard is 1 for the module-level
#     `if __name__ == "__main__":` header and everything inside it.
#     These rows are test scaffolding rather than program logic.
#   - loop_depth and nested_loop describe loops in the record's whole
#     subtree, body included, so an outer loop that contains another
#     loop is detectable from its header record.
#   - parent_statement_id is the statement_id of the nearest enclosing
#     If/For/While record in the same function or class scope, or blank
#     if there is none.
#   - enclosing_loop_depth is the number of For/While loops in the same
#     function or class scope whose body contains the record. A loop's
#     own header and its else block are not inside the loop body.
#   - similarity_group is the program's near-duplicate group (see
#     validate_corpus.similarity_groups). Split train and test data by
#     this column, not by row or program_id.
#
# statement_id numbers records 1..n per program in source order, so IDs
# are deterministic for a given corpus file.


# =========================================================
# MANIFEST HANDLING
# =========================================================

def normalize_header(header):
    """Normalize common CSV header formatting artifacts."""
    header = html.unescape(header or "")
    header = header.replace("\ufeff", "").strip()
    header = header.strip("*").strip()
    return re.sub(r"\s+", "_", header.lower())


def read_manifest():
    if not MANIFEST_FILE.is_file():
        raise FileNotFoundError(
            f"Manifest not found: {MANIFEST_FILE}\n"
            "Check that manifest.csv is inside program_corpus."
        )

    with MANIFEST_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("The manifest CSV has no header row.")

        original_headers = reader.fieldnames
        normalized_headers = [
            normalize_header(header) for header in original_headers
        ]

        if len(normalized_headers) != len(set(normalized_headers)):
            raise ValueError(
                "The manifest contains duplicate column names after "
                "normalization. Check its header row."
            )

        records = []

        for raw_record in reader:
            record = {}

            for original, normalized in zip(
                original_headers, normalized_headers
            ):
                value = raw_record.get(original, "")
                record[normalized] = (value or "").strip()

            # Accept a few common column-name variations.
            if not record.get("program_id"):
                record["program_id"] = (
                    record.get("id", "")
                    or record.get("program", "")
                )

            if not record.get("filename"):
                record["filename"] = (
                    record.get("file_name", "")
                    or record.get("file", "")
                )

            if not record.get("program_id") and record.get("filename"):
                record["program_id"] = Path(
                    record["filename"]
                ).stem

            if not record.get("program_id"):
                raise ValueError(
                    "A manifest row has no program_id or usable filename."
                )

            if not record.get("filename"):
                record["filename"] = record["program_id"] + ".py"

            records.append(record)

    ids = [record["program_id"] for record in records]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate program_id values found in manifest.csv."
        )

    filenames = [record["filename"] for record in records]

    if len(filenames) != len(set(filenames)):
        raise ValueError(
            "Duplicate filenames found in manifest.csv."
        )

    return records


# =========================================================
# AST FEATURE EXTRACTION
# =========================================================

class FeatureExtractor(ast.NodeVisitor):
    """Extract syntactic operator and operand counts."""

    def __init__(self):
        self.operator_count = 0
        self.operand_count = 0
        self.condition_count = 0
        self.logical_operator_count = 0

    def visit_BinOp(self, node):
        self.operator_count += 1
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.operator_count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.operator_count += len(node.values) - 1
        self.logical_operator_count += len(node.values) - 1
        self.condition_count += len(node.values) - 1
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.operator_count += len(node.ops)
        self.condition_count += len(node.ops)
        self.generic_visit(node)

    def visit_Name(self, node):
        self.operand_count += 1

    def visit_Constant(self, node):
        self.operand_count += 1


def calculate_expression_depth(node):
    """Return the maximum expression-tree depth."""
    if not isinstance(node, ast.expr):
        return 0

    children = [
        child
        for child in ast.iter_child_nodes(node)
        if isinstance(child, ast.expr)
    ]

    if not children:
        return 1

    return 1 + max(
        calculate_expression_depth(child) for child in children
    )


def get_loop_nodes(node):
    loop_types = (ast.For, ast.While, ast.AsyncFor)

    return [
        child for child in ast.walk(node)
        if isinstance(child, loop_types)
    ]


def calculate_subtree_loop_depth(node):
    """
    Calculate the deepest loop nesting within this statement's subtree.
    This is not the number of loops enclosing the statement in the file.
    """
    loop_types = (ast.For, ast.While, ast.AsyncFor)
    maximum = 0

    def visit(current, depth):
        nonlocal maximum

        if isinstance(current, loop_types):
            depth += 1
            maximum = max(maximum, depth)

        for child in ast.iter_child_nodes(current):
            visit(child, depth)

    visit(node, 0)
    return maximum


def has_nested_loop(node):
    """True if this loop statement contains another loop beneath it."""
    loop_types = (ast.For, ast.While, ast.AsyncFor)

    if not isinstance(node, loop_types):
        return False

    return sum(
        isinstance(child, loop_types)
        for child in ast.walk(node)
    ) > 1


def count_atomic_conditions(test):
    """
    Count the atomic conditions in an if/while test.

    - and / or: the sum of the counts of its operands;
    - not: the count of its operand;
    - comparison: one per comparison operator, so the chained
      comparison 0 <= x < n counts 2;
    - any other expression (name, call, attribute, constant, ...): 1.

    Boolean expressions nested inside a call, subscript or conditional
    expression are not unpacked; that enclosing expression counts 1.
    """
    if isinstance(test, ast.BoolOp):
        return sum(count_atomic_conditions(value) for value in test.values)

    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return count_atomic_conditions(test.operand)

    if isinstance(test, ast.Compare):
        return len(test.ops)

    return 1


def has_complex_conditional(node):
    """
    Initial heuristic (a candidate label, not ground truth): an if or
    while test with at least COMPLEX_CONDITION_THRESHOLD atomic
    conditions.
    """
    if not isinstance(node, (ast.If, ast.While)):
        return False

    return (
        count_atomic_conditions(node.test)
        >= COMPLEX_CONDITION_THRESHOLD
    )


def is_docstring(stmt, owner):
    """True if stmt is the docstring of a module, class or function."""
    return (
        isinstance(owner, (ast.Module,) + SCOPE_STATEMENTS)
        and bool(owner.body)
        and owner.body[0] is stmt
        and isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def statement_length(code):
    """Length of code with its line breaks joined as on a single line."""
    flat = re.sub(r"(?<=[\[({])\s*\\?\n\s*|\s*\\?\n\s*(?=[\])}])", "", code)
    return len(re.sub(r"\s*\\?\n\s*", " ", flat))


def is_long_statement(node, code):
    """
    Initial heuristic (a candidate label, not ground truth): a simple
    statement whose statement_length is above LONG_STATEMENT_THRESHOLD
    characters. Compound-statement headers are never long statements.
    """
    if not isinstance(node, SIMPLE_STATEMENTS):
        return False

    return statement_length(code) > LONG_STATEMENT_THRESHOLD


def main_guard_lines(tree):
    """Line ranges of module-level `if __name__ == "__main__":` blocks."""
    return [
        (node.lineno, node.end_lineno)
        for node in tree.body
        if isinstance(node, ast.If)
        and "__name__" in ast.unparse(node.test)
        and "__main__" in ast.unparse(node.test)
    ]


def to_char_col(line, byte_col):
    """Convert an AST UTF-8 byte offset into a str index for line."""
    return len(line.encode("utf-8")[:byte_col].decode("utf-8", "ignore"))


def header_colon_position(node, source_lines):
    """
    (line, char col) of the colon that ends an if/for/while header.

    Scanning starts after the last header expression and skips closing
    brackets, whitespace, line continuations and comments.
    """
    last_part = header_parts(node)[-1]
    line_no = last_part.end_lineno
    col = to_char_col(source_lines[line_no - 1], last_part.end_col_offset)

    while line_no <= len(source_lines):
        line = source_lines[line_no - 1]

        while col < len(line):
            char = line[col]

            if char == ":":
                return line_no, col
            if char == "#":
                break
            col += 1

        line_no += 1
        col = 0

    raise ValueError(
        f"No header colon found for {type(node).__name__} "
        f"at line {node.lineno}"
    )


def record_span(node, source_lines):
    """
    Start and end (line, char col) of the source a record represents,
    end exclusive: the whole simple statement, or a compound header up
    to and including its colon.
    """
    start = (
        node.lineno,
        to_char_col(source_lines[node.lineno - 1], node.col_offset),
    )

    if isinstance(node, HEADER_STATEMENTS):
        colon_line, colon_col = header_colon_position(node, source_lines)
        return start, (colon_line, colon_col + 1)

    end = (
        node.end_lineno,
        to_char_col(source_lines[node.end_lineno - 1], node.end_col_offset),
    )
    return start, end


def source_text(source_lines, start, end):
    (start_line, start_col), (end_line, end_col) = start, end

    if start_line == end_line:
        return source_lines[start_line - 1][start_col:end_col]

    parts = [source_lines[start_line - 1][start_col:]]
    parts.extend(source_lines[start_line:end_line - 1])
    parts.append(source_lines[end_line - 1][:end_col])
    return "".join(parts)


def header_parts(node):
    """The AST expressions a record's statement-level features cover."""
    if isinstance(node, (ast.If, ast.While)):
        return [node.test]

    if isinstance(node, (ast.For, ast.AsyncFor)):
        return [node.target, node.iter]

    return [
        child
        for child in ast.iter_child_nodes(node)
        if isinstance(child, ast.expr)
    ]


def nested_blocks(stmt):
    """Statement lists nested in a non-record statement, in source order."""
    yield getattr(stmt, "body", [])

    for child in getattr(stmt, "handlers", []) + getattr(stmt, "cases", []):
        yield child.body

    yield getattr(stmt, "orelse", [])
    yield getattr(stmt, "finalbody", [])


def extract_statements(tree, source_lines):
    statements = []
    spans = []
    main_guards = main_guard_lines(tree)

    def emit(node, parent_id, enclosing_loops):
        start, end = record_span(node, source_lines)
        code = source_text(source_lines, start, end).strip()

        parts = header_parts(node)

        extractor = FeatureExtractor()
        if isinstance(node, SIMPLE_STATEMENTS):
            extractor.visit(node)
        else:
            for part in parts:
                extractor.visit(part)

        expression_depth = max(
            (calculate_expression_depth(part) for part in parts),
            default=0,
        )

        statement_id = len(statements) + 1

        statements.append({
            "statement_id": statement_id,
            "parent_statement_id": "" if parent_id is None else parent_id,
            "enclosing_loop_depth": enclosing_loops,
            "line_no": start[0],
            "end_line": end[0],
            "in_main_guard": int(any(
                first <= start[0] <= last for first, last in main_guards
            )),
            "statement_type": type(node).__name__,
            "code": code,
            "statement_length": statement_length(code),
            "operator_count": extractor.operator_count,
            "operand_count": extractor.operand_count,
            "expression_depth": expression_depth,
            "loop_depth": calculate_subtree_loop_depth(node),
            "condition_count": extractor.condition_count,
            "logical_operator_count": extractor.logical_operator_count,

            # These are rule-generated candidate labels,
            # not independently verified ground truth.
            "long_statement": int(
                is_long_statement(node, code)
            ),
            "nested_loop": int(has_nested_loop(node)),
            "complex_conditional": int(
                has_complex_conditional(node)
            ),
        })
        spans.append((start, end))

        return statement_id

    def visit_block(block, owner, parent_id, enclosing_loops):
        for stmt in block:
            if is_docstring(stmt, owner):
                continue
            visit_statement(stmt, parent_id, enclosing_loops)

    def visit_statement(stmt, parent_id, enclosing_loops):
        if isinstance(stmt, SIMPLE_STATEMENTS):
            emit(stmt, parent_id, enclosing_loops)

        elif isinstance(stmt, ast.If):
            own_id = emit(stmt, parent_id, enclosing_loops)
            visit_block(stmt.body, stmt, own_id, enclosing_loops)
            visit_block(stmt.orelse, stmt, own_id, enclosing_loops)

        elif isinstance(stmt, LOOP_STATEMENTS):
            own_id = emit(stmt, parent_id, enclosing_loops)
            visit_block(stmt.body, stmt, own_id, enclosing_loops + 1)
            visit_block(stmt.orelse, stmt, own_id, enclosing_loops)

        elif isinstance(stmt, SCOPE_STATEMENTS):
            visit_block(stmt.body, stmt, None, 0)

        else:
            for block in nested_blocks(stmt):
                visit_block(block, stmt, parent_id, enclosing_loops)

    visit_block(tree.body, tree, None, 0)

    check_record_spans(spans)

    return statements


def count_docstrings(tree):
    owners = [tree] + [
        node for node in ast.walk(tree)
        if isinstance(node, SCOPE_STATEMENTS)
    ]
    return sum(
        bool(owner.body) and is_docstring(owner.body[0], owner)
        for owner in owners
    )


def check_record_spans(spans):
    """Records must be in source order and must not share source text."""
    for (_, previous_end), (start, _) in zip(spans, spans[1:]):
        if start < previous_end:
            raise ValueError(
                f"Overlapping or out-of-order records: a record starts at "
                f"{start} before the previous one ends at {previous_end}"
            )


# =========================================================
# CORPUS AND MANIFEST CONSISTENCY CHECKS
# =========================================================

def validate_corpus_manifest(manifest_records, python_files):
    manifest_by_filename = {
        Path(record["filename"]).name: record
        for record in manifest_records
    }

    files_by_name = {path.name: path for path in python_files}

    missing_files = sorted(
        set(manifest_by_filename) - set(files_by_name)
    )

    unlisted_files = sorted(
        set(files_by_name) - set(manifest_by_filename)
    )

    if missing_files or unlisted_files:
        details = ["Manifest/corpus mismatch detected."]

        if missing_files:
            details.append(
                "Files listed in manifest but not found: "
                + ", ".join(missing_files[:20])
            )

        if unlisted_files:
            details.append(
                "Python files missing from manifest: "
                + ", ".join(unlisted_files[:20])
            )

        raise ValueError("\n".join(details))

    return manifest_by_filename


# =========================================================
# MAIN DATASET GENERATION
# =========================================================

def main():
    print("=" * 60)
    print("S7 CORPUS-WIDE DATASET GENERATION")
    print("=" * 60)

    if not CORPUS_DIR.is_dir():
        raise FileNotFoundError(
            f"Python corpus folder not found: {CORPUS_DIR}"
        )

    manifest_records = read_manifest()
    python_files = sorted(CORPUS_DIR.glob("*.py"))

    if not python_files:
        raise ValueError(
            f"No Python files found in {CORPUS_DIR}"
        )

    manifest_by_filename = validate_corpus_manifest(
        manifest_records, python_files
    )

    groups = similarity_groups(python_files)

    all_rows = []
    syntax_errors = []
    docstrings_excluded = 0

    # Provenance fields retained from the manifest.
    metadata_fields = [
        "domain",
        "task_description",
        "intended_category",
        "model_name",
        "prompt_version",
        "generation_batch",
        "syntax_valid",
        "review_status",
    ]

    for file_path in python_files:
        program_id = file_path.stem
        manifest_record = manifest_by_filename[file_path.name]

        source_code = file_path.read_text(encoding="utf-8")

        if not source_code.strip():
            syntax_errors.append(
                f"{file_path.name}: empty file"
            )
            continue

        try:
            tree = ast.parse(
                source_code,
                filename=file_path.name
            )
        except SyntaxError as error:
            syntax_errors.append(
                f"{file_path.name}: {error}"
            )
            continue

        source_lines = source_code.splitlines(keepends=True)

        statements = extract_statements(tree, source_lines)
        docstrings_excluded += count_docstrings(tree)

        for statement in statements:
            row = {
                "program_id": program_id,
                "filename": file_path.name,
                "similarity_group": groups[program_id],
                **{
                    field: manifest_record.get(field, "")
                    for field in metadata_fields
                },
                **statement,
            }

            all_rows.append(row)

    if syntax_errors:
        print("\nERROR: Some files could not be processed:")
        for error in syntax_errors:
            print(" -", error)

        raise RuntimeError(
            "Dataset generation stopped. Fix the listed files "
            "and rerun the script."
        )

    if not all_rows:
        raise ValueError(
            "No supported statements were extracted from the corpus."
        )

    fieldnames = [
        "program_id",
        "filename",
        "similarity_group",
        *metadata_fields,
        "statement_id",
        "parent_statement_id",
        "enclosing_loop_depth",
        "statement_type",
        "line_no",
        "end_line",
        "in_main_guard",
        "code",
        "statement_length",
        "operator_count",
        "operand_count",
        "expression_depth",
        "loop_depth",
        "condition_count",
        "logical_operator_count",
        "long_statement",
        "nested_loop",
        "complex_conditional",
    ]

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nDataset generation completed.")
    print("Manifest records:", len(manifest_records))
    print("Python files processed:", len(python_files))
    print("Statement records:", len(all_rows))
    print("Docstrings excluded (not records):", docstrings_excluded)
    print("Similarity groups:", len(set(groups.values())))
    print("Output file:", OUTPUT_FILE)

    print("\nRule-generated statement label distribution:")
    for label in (
        "long_statement",
        "nested_loop",
        "complex_conditional",
    ):
        positive = sum(row[label] == 1 for row in all_rows)
        negative = len(all_rows) - positive

        print(
            f"{label}: positive={positive}, "
            f"negative={negative}"
        )

    print("\nImportant:")
    print("- Manifest categories remain program-level metadata.")
    print("- AST labels are heuristic candidates, not verified ground truth.")
    print("- Review label definitions and samples before model training.")


if __name__ == "__main__":
    main()