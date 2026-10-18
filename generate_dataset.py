
import ast
import csv


SOURCE_FILE = "examples.py"
OUTPUT_FILE = "dataset.csv"

# Initial prototype threshold.
# This should be justified or tuned during later experiments.
LONG_STATEMENT_THRESHOLD = 60


# ---------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------

class FeatureExtractor(ast.NodeVisitor):

    def __init__(self):
        self.operator_count = 0
        self.operand_count = 0
        self.condition_count = 0
        self.logical_operator_count = 0

    def visit_BinOp(self, node):
        self.operator_count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.logical_operator_count += len(node.values) - 1
        self.condition_count += len(node.values)
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.condition_count += len(node.ops)
        self.operator_count += len(node.ops)
        self.generic_visit(node)

    def visit_Name(self, node):
        self.operand_count += 1

    def visit_Constant(self, node):
        self.operand_count += 1


# ---------------------------------------------------------
# Calculate expression depth
# ---------------------------------------------------------

def calculate_expression_depth(node):

    if isinstance(node, ast.expr):
        children = [
            child
            for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.expr)
        ]

        if not children:
            return 1

        return 1 + max(
            calculate_expression_depth(child)
            for child in children
        )

    return 0


# ---------------------------------------------------------
# Calculate maximum loop nesting depth
# ---------------------------------------------------------

def calculate_loop_depth(node, current_depth=0):

    max_depth = current_depth

    for child in ast.iter_child_nodes(node):

        if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
            child_depth = current_depth + 1

            max_depth = max(
                max_depth,
                calculate_loop_depth(child, child_depth)
            )
        else:
            max_depth = max(
                max_depth,
                calculate_loop_depth(child, current_depth)
            )

    return max_depth


# ---------------------------------------------------------
# Determine whether a loop contains another loop
# ---------------------------------------------------------

def has_nested_loop(node):

    loop_types = (ast.For, ast.While, ast.AsyncFor)

    for child in ast.iter_child_nodes(node):

        if isinstance(child, loop_types):
            return True

        if has_nested_loop(child):
            return True

    return False


# ---------------------------------------------------------
# Determine whether an if-condition is complex
# ---------------------------------------------------------

def has_complex_conditional(node):

    if not isinstance(node, ast.If):
        return False

    condition = node.test

    logical_operator_count = sum(
        len(child.values) - 1
        for child in ast.walk(condition)
        if isinstance(child, ast.BoolOp)
    )

    comparison_count = sum(
        len(child.ops)
        for child in ast.walk(condition)
        if isinstance(child, ast.Compare)
    )

    # Initial operational definition:
    # multiple comparisons, or a condition combining
    # multiple Boolean operands.
    return (
        logical_operator_count >= 1
        and comparison_count >= 2
    ) or comparison_count >= 3


# ---------------------------------------------------------
# Determine whether a statement is long
# ---------------------------------------------------------

def is_long_statement(node, code):

    # Do not classify complete control-flow blocks as
    # long statements based on their total line length.
    if isinstance(
        node,
        (
            ast.If,
            ast.For,
            ast.While,
            ast.AsyncFor,
            ast.FunctionDef
        )
    ):
        return False

    return len(code.strip()) > LONG_STATEMENT_THRESHOLD


# ---------------------------------------------------------
# Extract source statements and features
# ---------------------------------------------------------

def extract_statements(tree, source_lines):

    statements = []

    supported_types = (
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

    for node in ast.walk(tree):

        if not isinstance(node, supported_types):
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

        # Calculate expression depth only from expressions
        # belonging directly to this statement.
        expressions = [
            child
            for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.expr)
        ]

        expression_depth = max(
            (
                calculate_expression_depth(expression)
                for expression in expressions
            ),
            default=0
        )

        # For loop statements, this includes their body.
        # It is useful as a structural feature, but the
        # statement's own loop nesting label is separate.
        loop_depth = calculate_loop_depth(node)

        nested_loop = (
            isinstance(node, (ast.For, ast.While, ast.AsyncFor))
            and has_nested_loop(node)
        )

        complex_conditional = has_complex_conditional(node)

        long_statement = is_long_statement(node, code)

        statements.append({
            "code": code,
            "line_no": start_line,
            "statement_length": len(code),
            "operator_count": extractor.operator_count,
            "operand_count": extractor.operand_count,
            "expression_depth": expression_depth,
            "loop_depth": loop_depth,
            "condition_count": extractor.condition_count,
            "logical_operator_count": extractor.logical_operator_count,
            "long_statement": int(long_statement),
            "nested_loop": int(nested_loop),
            "complex_conditional": int(complex_conditional)
        })

    return statements


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

def main():

    with open(SOURCE_FILE, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)
    source_lines = source_code.splitlines(keepends=True)

    statements = extract_statements(tree, source_lines)

    for index, statement in enumerate(statements, start=1):
        statement["statement_id"] = index

    fieldnames = [
        "statement_id",
        "code",
        "line_no",
        "statement_length",
        "operator_count",
        "operand_count",
        "expression_depth",
        "loop_depth",
        "condition_count",
        "logical_operator_count",
        "long_statement",
        "nested_loop",
        "complex_conditional"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(statements)

    print("Dataset generated successfully.")
    print("Number of statements:", len(statements))
    print("Saved to:", OUTPUT_FILE)

    print("\nLabel distribution:")

    for label in (
        "long_statement",
        "nested_loop",
        "complex_conditional"
    ):
        positive = sum(row[label] == 1 for row in statements)
        negative = len(statements) - positive

        print(
            f"{label}: positive={positive}, "
            f"negative={negative}"
        )


if __name__ == "__main__":
    main()
