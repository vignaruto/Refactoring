
import ast
import contextlib
import io


# --------------------------------------------------
# 1. Syntax validation
# --------------------------------------------------

def check_syntax(source_code):
    try:
        ast.parse(source_code)
        return True
    except SyntaxError as error:
        print(f"Syntax error: {error}")
        return False


# --------------------------------------------------
# 2. Execute a function and capture its behaviour
# --------------------------------------------------

def execute_function(source_code, function_name, inputs):
    namespace = {}

    try:
        exec(compile(source_code, "<code>", "exec"), namespace)

        function = namespace[function_name]

        captured_output = io.StringIO()

        with contextlib.redirect_stdout(captured_output):
            return_value = function(*inputs)

        return {
            "success": True,
            "return_value": return_value,
            "printed_output": captured_output.getvalue(),
            "error": None
        }

    except Exception as error:
        return {
            "success": False,
            "return_value": None,
            "printed_output": None,
            "error": f"{type(error).__name__}: {error}"
        }


# --------------------------------------------------
# 3. Validate original against transformed code
# --------------------------------------------------

def validate_refactoring(
    original_code,
    transformed_code,
    function_name,
    test_inputs
):
    print("\n========== SYNTAX VALIDATION ==========")

    original_valid = check_syntax(original_code)
    transformed_valid = check_syntax(transformed_code)

    print(f"Original code valid:    {original_valid}")
    print(f"Transformed code valid: {transformed_valid}")

    if not original_valid or not transformed_valid:
        print("Validation failed: invalid Python syntax.")
        return False

    print("\n========== BEHAVIOURAL VALIDATION ==========")

    all_tests_passed = True

    for inputs in test_inputs:
        original_result = execute_function(
            original_code, function_name, inputs
        )

        transformed_result = execute_function(
            transformed_code, function_name, inputs
        )

        print(f"\nInput: {inputs}")

        if not original_result["success"]:
            print("Original code raised an exception:")
            print(original_result["error"])
            all_tests_passed = False
            continue

        if not transformed_result["success"]:
            print("Transformed code raised an exception:")
            print(transformed_result["error"])
            all_tests_passed = False
            continue

        return_matches = (
            original_result["return_value"]
            == transformed_result["return_value"]
        )

        output_matches = (
            original_result["printed_output"]
            == transformed_result["printed_output"]
        )

        print(f"Original return:    {original_result['return_value']}")
        print(f"Transformed return: {transformed_result['return_value']}")
        print(f"Return values match: {return_matches}")
        print(f"Printed output matches: {output_matches}")

        if not return_matches or not output_matches:
            all_tests_passed = False

    print("\n========== VALIDATION RESULT ==========")

    if all_tests_passed:
        print("PASS: All supplied test cases matched.")
    else:
        print("FAIL: At least one test case did not match.")

    return all_tests_passed


# --------------------------------------------------
# 4. Test both transformations together
# --------------------------------------------------

if __name__ == "__main__":

    original_code = '''
def example(a, b, c, d, e, f):
    result = a * b + c * d + e * f + a * c + b * d + c * e + d * f

    if a > b and b > c and c > d and d > e:
        print("condition satisfied")

    return result
'''

    transformed_code = '''
def example(a, b, c, d, e, f):
    _temp1 = a * b + c * d + e * f + a * c + b * d + c * e
    _temp2 = d * f
    result = _temp1 + _temp2

    _condition = a > b and b > c and c > d and d > e
    if _condition:
        print("condition satisfied")

    return result
'''

    test_inputs = [
        (2, 3, 4, 5, 6, 7),
        (5, 4, 3, 2, 1, 6),
        (1, 2, 3, 4, 5, 6),
        (10, 8, 6, 4, 2, 1)
    ]

    validate_refactoring(
        original_code,
        transformed_code,
        "example",
        test_inputs
    )
