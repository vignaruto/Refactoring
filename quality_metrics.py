
import ast

from transformation import transform_code


# --------------------------------------------------
# 1. Calculate expression depth
# --------------------------------------------------

def expression_depth(node):
    children = [
        child
        for child in ast.iter_child_nodes(node)
        if isinstance(child, ast.expr)
    ]

    if not children:
        return 1

    return 1 + max(expression_depth(child) for child in children)


# --------------------------------------------------
# 2. Calculate code quality metrics
# --------------------------------------------------

def calculate_metrics(source_code):
    tree = ast.parse(source_code)

    expression_lengths = []
    expression_depths = []
    logical_operator_count = 0
    temporary_variable_count = 0

    for node in ast.walk(tree):

        # Expression length and depth
        if isinstance(node, ast.expr):
            segment = ast.get_source_segment(source_code, node)

            if segment is not None:
                expression_lengths.append(len(segment))

            expression_depths.append(expression_depth(node))

        # Count Boolean operators in conditions
        if isinstance(node, ast.BoolOp):
            logical_operator_count += len(node.values) - 1

        # Count introduced temporary assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id.startswith(("_temp", "_condition"))
                ):
                    temporary_variable_count += 1

    return {
        "maximum_expression_length": max(expression_lengths, default=0),
        "maximum_expression_depth": max(expression_depths, default=0),
        "logical_operator_count": logical_operator_count,
        "temporary_variable_count": temporary_variable_count
    }


# --------------------------------------------------
# 3. Display before/after comparison
# --------------------------------------------------

def compare_metrics(original_code, transformed_code):
    before = calculate_metrics(original_code)
    after = calculate_metrics(transformed_code)

    print("\n========== QUALITY METRICS ==========")

    print(f"{'Metric':<32} {'Before':>10} {'After':>10}")
    print("-" * 54)

    for metric in before:
        print(
            f"{metric:<32} "
            f"{before[metric]:>10} "
            f"{after[metric]:>10}"
        )

    print("\n========== METRIC INTERPRETATION ==========")

    if (
        after["maximum_expression_length"]
        < before["maximum_expression_length"]
    ):
        print("Maximum expression length decreased.")
    else:
        print("Maximum expression length did not decrease.")

    if (
        after["maximum_expression_depth"]
        < before["maximum_expression_depth"]
    ):
        print("Maximum expression depth decreased.")
    else:
        print("Maximum expression depth did not decrease.")

    if (
        after["logical_operator_count"]
        < before["logical_operator_count"]
    ):
        print("Logical operator count decreased.")
    else:
        print("Logical operator count did not decrease.")

    print(
        "Temporary assignments introduced:",
        after["temporary_variable_count"]
        - before["temporary_variable_count"]
    )


# --------------------------------------------------
# 4. Run the actual transformer
# --------------------------------------------------

if __name__ == "__main__":

    original_code = '''
def example(a, b, c, d, e, f):
    result = a * b + c * d + e * f + a * c + b * d + c * e + d * f

    if a > b and b > c and c > d and d > e:
        print("condition satisfied")

    return result
'''

    # These line numbers match the original_code above.
    actions_by_line = {
        3: ["DECOMPOSE_EXPRESSION"],
        5: ["EXTRACT_CONDITION"]
    }

    transformed_code, applied_actions = transform_code(
        original_code,
        actions_by_line
    )

    print("Applied transformations:", applied_actions)

    compare_metrics(original_code, transformed_code)
