import ast
import csv
import re
import html
from pathlib import Path


# =========================================================
# S7 PROJECT: CORPUS-WIDE DATASET GENERATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

CORPUS_DIR = BASE_DIR / "program_corpus" / "programs"
MANIFEST_FILE = BASE_DIR / "program_corpus" / "manifest.csv"
OUTPUT_FILE = BASE_DIR / "dataset.csv"

LONG_STATEMENT_THRESHOLD = 60

SUPPORTED_STATEMENTS = (
    ast.Assign,
    ast.AnnAssign,
    ast.AugAssign,
    ast.Expr,
    ast.Return,
    ast.If,
    ast.For,
    ast.While,
    ast.AsyncFor,
)


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


def has_complex_conditional(node):
    """
    Operational heuristic:
    - at least one logical operator and at least two comparisons; OR
    - at least three comparisons.

    Applied to if statements only.
    """
    if not isinstance(node, ast.If):
        return False

    logical_count = sum(
        len(child.values) - 1
        for child in ast.walk(node.test)
        if isinstance(child, ast.BoolOp)
    )

    comparison_count = sum(
        len(child.ops)
        for child in ast.walk(node.test)
        if isinstance(child, ast.Compare)
    )

    return (
        (logical_count >= 1 and comparison_count >= 2)
        or comparison_count >= 3
    )


def is_long_statement(node, code):
    """
    Initial heuristic: more than 60 characters.
    Control-flow blocks and function definitions are excluded.
    """
    excluded_types = (
        ast.If,
        ast.For,
        ast.While,
        ast.AsyncFor,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )

    if isinstance(node, excluded_types):
        return False

    return len(code.strip()) > LONG_STATEMENT_THRESHOLD


def extract_statements(tree, source_lines):
    statements = []

    for node in ast.walk(tree):
        if not isinstance(node, SUPPORTED_STATEMENTS):
            continue

        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        code = "".join(
            source_lines[start_line - 1:end_line]
        ).strip()

        if not code:
            continue

        extractor = FeatureExtractor()
        extractor.visit(node)

        direct_expressions = [
            child
            for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.expr)
        ]

        expression_depth = max(
            (
                calculate_expression_depth(expression)
                for expression in direct_expressions
            ),
            default=0,
        )

        statements.append({
            "line_no": start_line,
            "end_line": end_line,
            "statement_type": type(node).__name__,
            "code": code,
            "statement_length": len(code),
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

    # Stable, human-readable ordering by source position.
    statements.sort(
        key=lambda row: (
            row["line_no"],
            row["end_line"],
            row["statement_type"],
        )
    )

    for index, statement in enumerate(statements, start=1):
        statement["statement_id"] = index

    return statements


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

    all_rows = []
    syntax_errors = []

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

        for statement in statements:
            row = {
                "program_id": program_id,
                "filename": file_path.name,
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
        *metadata_fields,
        "statement_id",
        "statement_type",
        "line_no",
        "end_line",
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