import sys
import textwrap
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import validation as val  # noqa: E402

ORIGINAL = textwrap.dedent("""\
    def score(a, b, c):
        if a > 1 and b > 2 and c > 3:
            return a * b + c
        return 0


    if __name__ == "__main__":
        assert score(2, 3, 4) == 10
        assert score(0, 3, 4) == 0
""")

REFACTORED = ORIGINAL.replace(
    "    if a > 1 and b > 2 and c > 3:\n",
    "    condition = a > 1 and b > 2 and c > 3\n    if condition:\n",
)


class SafetyTests(unittest.TestCase):
    def test_correct_refactoring_has_no_problems(self):
        self.assertEqual(val.safety_problems(ORIGINAL, REFACTORED), [])

    def test_structural_changes_are_reported(self):
        cases = {
            "signatures": ORIGINAL.replace("def score(a, b, c)", "def score(a, b, c=1)"),
            "__main__": ORIGINAL.replace("== 10", "== 10.0"),
            "imports": "import os\n" + ORIGINAL,
            "call counts": ORIGINAL.replace("return a * b + c", "return max(a * b + c, 0)"),
        }
        for expected, changed in cases.items():
            with self.subTest(expected):
                problems = " ".join(val.safety_problems(ORIGINAL, changed))
                self.assertIn(expected, problems)

    def test_itertools_import_and_product_call_are_allowed(self):
        changed = "import itertools\n" + ORIGINAL.replace(
            "    return 0\n", "    for x, y in itertools.product([1], [2]):\n        pass\n    return 0\n"
        )
        self.assertEqual(val.safety_problems(ORIGINAL, changed), [])


class ValidateProgramTests(unittest.TestCase):
    def test_correct_refactoring_is_valid(self):
        report = val.validate_program(ORIGINAL, REFACTORED)
        self.assertTrue(report["valid"], report["reasons"])
        self.assertEqual(report["self_test"], "pass")
        self.assertGreater(report["differential"]["calls"], 2)

    def test_fault_missed_by_self_test_is_caught_by_variants(self):
        faulty = REFACTORED.replace("c > 3", "c >= 3")
        report = val.validate_program(ORIGINAL, faulty)
        self.assertEqual(report["self_test"], "pass")
        self.assertFalse(report["valid"])
        self.assertTrue(report["differential"]["mismatches"])

    def test_failing_self_test_and_syntax_error(self):
        report = val.validate_program(ORIGINAL, REFACTORED.replace("return a * b + c", "return a * b - c"))
        self.assertFalse(report["valid"])
        self.assertIn("AssertionError", report["self_test"])
        report = val.validate_program(ORIGINAL, "def score(:\n")
        self.assertFalse(report["valid"])

    def test_explicit_calls_without_self_test(self):
        original = "def f(a, b):\n    return a + b * 2\n"
        report = val.validate_program(original, "def f(a, b):\n    return a + b + b\n",
                                      [["f", [1, 2]]])
        self.assertTrue(report["valid"], report["reasons"])
        self.assertEqual(report["self_test"], "none")
        report = val.validate_program(original, "def f(a, b):\n    return a * b * 2\n",
                                      [["f", [1, 2]]])
        self.assertFalse(report["valid"])

    def test_class_methods_are_compared_by_trace(self):
        original = textwrap.dedent("""\
            class Counter:
                def __init__(self):
                    self.total = 0

                def add(self, a, b):
                    self.total += a * 2 + b
                    return self.total


            if __name__ == "__main__":
                c = Counter()
                c.add(1, 2)
                assert c.total >= 0
        """)
        faulty = original.replace("a * 2 + b", "a * 3 + b")
        self.assertTrue(val.validate_program(original, original)["valid"])
        report = val.validate_program(original, faulty)
        self.assertFalse(report["valid"])


class VariantTests(unittest.TestCase):
    def test_variants_cover_edge_cases(self):
        self.assertIn(0, val.variants_of(5))
        self.assertIn([], val.variants_of([1, 2, 3]))
        self.assertIn({"b": 2}, val.variants_of({"a": 1, "b": 2}))
        self.assertIn([0, 2, 3], val.variants_of([1, 2, 3]))
        self.assertEqual(val.variants_of(None), [])


class MutationTests(unittest.TestCase):
    def test_faults_are_planted_only_in_refactored_lines(self):
        found = dict(val.mutants(ORIGINAL, REFACTORED))
        self.assertIn("swap and/or", found)
        self.assertIn("condition = a > 1 or b > 2 or c > 3", found["swap and/or"])
        self.assertIn("negate extracted condition", found)
        self.assertNotIn("change arithmetic operator", found)


if __name__ == "__main__":
    unittest.main()
