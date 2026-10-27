
import ast

# (action, statement type) pairs RefactoringTransformer applies.
SUPPORTED_ACTIONS = {
    ("DECOMPOSE_EXPRESSION", "Assign"),
    ("EXTRACT_CONDITION", "If"),
}


class RefactoringTransformer(ast.NodeTransformer):

    def __init__(self, actions_by_line):
        self.actions_by_line = actions_by_line
        self.applied_actions = []

    def visit_Assign(self, node):
        self.generic_visit(node)

        actions = self.actions_by_line.get(node.lineno, [])

        if (
            "DECOMPOSE_EXPRESSION" in actions
            and isinstance(node.value, ast.BinOp)
        ):
            expression = node.value

            temp1 = ast.Assign(
                targets=[
                    ast.Name(id="_temp1", ctx=ast.Store())
                ],
                value=expression.left
            )

            temp2 = ast.Assign(
                targets=[
                    ast.Name(id="_temp2", ctx=ast.Store())
                ],
                value=expression.right
            )

            new_assignment = ast.Assign(
                targets=node.targets,
                value=ast.BinOp(
                    left=ast.Name(id="_temp1", ctx=ast.Load()),
                    op=expression.op,
                    right=ast.Name(id="_temp2", ctx=ast.Load())
                )
            )

            for new_node in (temp1, temp2, new_assignment):
                ast.copy_location(new_node, node)

            self.applied_actions.append("DECOMPOSE_EXPRESSION")

            return [temp1, temp2, new_assignment]

        return node

    def visit_If(self, node):
        self.generic_visit(node)

        actions = self.actions_by_line.get(node.lineno, [])

        if "EXTRACT_CONDITION" in actions:
            condition_assignment = ast.Assign(
                targets=[
                    ast.Name(id="_condition", ctx=ast.Store())
                ],
                value=node.test
            )

            new_if = ast.If(
                test=ast.Name(id="_condition", ctx=ast.Load()),
                body=node.body,
                orelse=node.orelse
            )

            ast.copy_location(condition_assignment, node)
            ast.copy_location(new_if, node)

            self.applied_actions.append("EXTRACT_CONDITION")

            return [condition_assignment, new_if]

        return node


def transform_code(source_code, actions_by_line):
    tree = ast.parse(source_code)

    transformer = RefactoringTransformer(actions_by_line)
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)

    transformed_code = ast.unparse(tree)

    return transformed_code, transformer.applied_actions


if __name__ == "__main__":

    source_code = """
def example(a, b, c, d, e, f):
    result = a * b + c * d + e * f + a * c + b * d + c * e + d * f

    if a > b and b > c and c > d and d > e:
        print("condition satisfied")

    return result
"""

    # Line numbers refer to the original source code.
    actions_by_line = {
        3: ["DECOMPOSE_EXPRESSION"],
        5: ["EXTRACT_CONDITION"]
    }

    transformed_code, applied_actions = transform_code(
        source_code,
        actions_by_line
    )

    print("\n========== ORIGINAL CODE ==========")
    print(source_code)

    print("\n========== REFACTORED CODE ==========")
    print(transformed_code)

    print("\n========== APPLIED ACTIONS ==========")
    for action in applied_actions:
        print("-", action)
