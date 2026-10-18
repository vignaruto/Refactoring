import ast
import csv


SOURCE_FILE = "examples.py"
OUTPUT_FILE = "dataset.csv"


# ---------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------

class FeatureExtractor(ast.NodeVisitor):

    def __init__(self):
        self.operator_count = 0
        self.operand_count = 0
        self.expression_depth = 0
        self.condition_count = 0
        self.logical_operator_count = 0

    def visit_BinOp(self, node):
        self.operator_count += 1
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolOp(self, node):
        self.logical_operator_count += len(node.values) - 1
        self.condition_count += len(node.values)

        for value in node.values:
            self.visit(value)

    def visit_Compare(self, node):
        self.condition_count += len(node.ops)
        self.operator_count += len(node.ops)

        self.visit(node.left)

        for comparator in node.comparators:
            self.visit(comparator)

    def visit_Name(self, node):
        self.operand_count += 1

    def visit_Constant(self, node):
        self.operand_count += 1


# ---------------------------------------------------------
# Calculate expression depth
# ---------------------------------------------------------

def calculate_expression_depth(node):

    if isinstance(node, ast.AST):

        children = list(ast.iter_child_nodes(node))

        if not children:
            return 1

        return 1 + max(
            calculate_expression_depth(child)
            for child in children
        )

    return 0


# ---------------------------------------------------------
# Calculate loop nesting depth
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
# Determine whether a statement contains nested loops
# ---------------------------------------------------------

def has_nested_loop(node):

    def search(current_node, depth):

        if isinstance(current_node, (ast.For, ast.While, ast.AsyncFor)):
            depth += 1

            if depth >= 2:
                return True

        for child in ast.iter_child_nodes(current_node):

            if search(child, depth):
                return True

        return False

    return search(node, 0)


# ---------------------------------------------------------
# Determine whether statement contains a complex conditional
# ---------------------------------------------------------

def has_complex_conditional(node):

    if isinstance(node, ast.If):

        condition = node.test

        logical_operators = sum(
            1
            for child in ast.walk(condition)
            if isinstance(child, ast.BoolOp)
        )

        comparisons = sum(
            1
            for child in ast.walk(condition)
            if isinstance(child, ast.Compare)
        )

        if logical_operators >= 1 or comparisons >= 2:
            return True

    return False


# ---------------------------------------------------------
# Determine whether statement is a long statement
# ---------------------------------------------------------

def is_long_statement(source_code):

    # Initial prototype threshold.
    # We will refine this later using literature/data analysis.

    return len(source_code.strip()) > 60


# ---------------------------------------------------------
# Extract statements
# ---------------------------------------------------------

def extract_statements(tree, source_lines):

    statements = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
                ast.Expr,
                ast.Return,
                ast.If,
                ast.For,
                ast.While,
                ast.AsyncFor,
                ast.FunctionDef,
            )
        ):

            if not hasattr(node, "lineno"):
                continue

            start_line = node.lineno
            end_line = getattr(node, "end_lineno", start_line)

            code = "".join(
                source_lines[start_line - 1:end_line]
            ).strip()

            # Ignore function definitions for the ML dataset
            if isinstance(node, ast.FunctionDef):
                continue

            extractor = FeatureExtractor()
            extractor.visit(node)

            statement_length = len(code)

            expression_depth = calculate_expression_depth(node)

            loop_depth = calculate_loop_depth(node)

            nested_loop = has_nested_loop(node)

            complex_conditional = has_complex_conditional(node)

            long_statement = is_long_statement(code)

            statements.append({
                "code": code,
                "line_no": start_line,
                "statement_length": statement_length,
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

    # Read source code
    with open(SOURCE_FILE, "r", encoding="utf-8") as file:
        source_code = file.read()

    # Parse using Python AST
    tree = ast.parse(source_code)

    source_lines = source_code.splitlines(keepends=True)

    # Extract statements and features
    statements = extract_statements(
        tree,
        source_lines
    )

    # Add statement IDs
    for index, statement in enumerate(statements, start=1):
        statement["statement_id"] = index

    # Column order
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

    # Write CSV
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
    print(f"Number of statements: {len(statements)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()