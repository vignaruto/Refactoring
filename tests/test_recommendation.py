import ast
import sys
import textwrap
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import recommendation as rec  # noqa: E402


def statement(source):
    return ast.parse(textwrap.dedent(source)).body[0]


def issue(source, statement_type, label, line_no=1, in_main_guard=0):
    return {
        "program_id": "P1", "filename": "P1.py", "statement_id": 1,
        "line_no": line_no, "end_line": line_no, "statement_type": statement_type,
        "in_main_guard": in_main_guard, "code": textwrap.dedent(source).strip(),
        "detected_issues": [label], "confidence": {label: 0.9},
    }


class LongStatementActionTests(unittest.TestCase):
    CASES = [
        ("x = a * b + c", "DECOMPOSE_EXPRESSION"),
        ("x += a * b", "DECOMPOSE_EXPRESSION"),
        ("return a + b", "DECOMPOSE_EXPRESSION"),
        ("ok = a > b and c > d", "DECOMPOSE_BOOLEAN"),
        ("ok = a < b", "DECOMPOSE_BOOLEAN"),
        ("x = f(a, b)", "EXTRACT_ARGUMENTS"),
        ("f(a, b)", "EXTRACT_ARGUMENTS"),
        ("x = [a, b]", "EXTRACT_ELEMENTS"),
        ("return {'a': a}", "EXTRACT_ELEMENTS"),
        ("x = a if c else b", "REPLACE_CONDITIONAL_EXPRESSION"),
        ("x = [v for v in a]", "SIMPLIFY_COMPREHENSION"),
        ("x = a[b]", "INTRODUCE_EXPLAINING_VARIABLE"),
    ]

    def test_action_follows_value_shape(self):
        for source, expected in self.CASES:
            with self.subTest(source=source):
                action, _ = rec.long_statement_action(statement(source))
                self.assertEqual(action, expected)


class NestedLoopActionTests(unittest.TestCase):
    def action(self, source):
        return rec.nested_loop_action(statement(source))[0]

    def test_independent_perfect_nesting_flattens(self):
        self.assertEqual(self.action("""
            for i in xs:
                for j in ys:
                    total += i * j
        """), "FLATTEN_WITH_PRODUCT")

    def test_unsafe_cases_extract_inner_loop(self):
        cases = {
            "inner depends on outer": """
                for i in xs:
                    for j in range(i):
                        total += j
            """,
            "break": """
                for i in xs:
                    for j in ys:
                        if j:
                            break
            """,
            "loop else": """
                for i in xs:
                    for j in ys:
                        pass
                    else:
                        pass
            """,
            "extra statement": """
                for i in xs:
                    row = []
                    for j in ys:
                        row.append(j)
            """,
            "while": """
                while xs:
                    for j in ys:
                        pass
            """,
        }
        for name, source in cases.items():
            with self.subTest(name):
                self.assertEqual(self.action(source), "EXTRACT_INNER_LOOP")


class RecommendRefactoringsTests(unittest.TestCase):
    SOURCE = textwrap.dedent("""\
        def f(a, b, c, d):
            if a > b and b > c and c > d:
                return 1
            elif a < b and b < c and c < d:
                return 2
            while a and b and c:
                a -= 1
            return 0

        if __name__ == "__main__":
            assert f(1, 2, 3, 4) == 2 and f(4, 3, 2, 1) == 1 and f(0, 0, 0, 0) == 0
    """)

    def recommend(self, issues):
        return rec.recommend_refactorings(issues, lambda issue: self.SOURCE)

    def test_if_and_elif_are_automatable_while_is_not(self):
        results = self.recommend([
            issue("if ...", "If", "complex_conditional", line_no=2),
            issue("elif ...", "If", "complex_conditional", line_no=4),
            issue("while ...", "While", "complex_conditional", line_no=6),
        ])
        found = [(r["recommendations"][0]["action"], r["recommendations"][0]["automatable"])
                 for r in results]
        self.assertEqual(found, [
            ("EXTRACT_CONDITION", True),
            ("EXTRACT_CONDITION", True),
            ("EXTRACT_PREDICATE", False),
        ])
        self.assertEqual(results[0]["recommendations"][0]["severity"],
                         {"measure": "atomic_conditions", "value": 3, "flagged_at": 3})

    def test_main_guard_issue_is_left_unchanged(self):
        result = self.recommend([
            issue("if __name__ ...", "If", "complex_conditional", line_no=10,
                  in_main_guard=1),
        ])[0]["recommendations"][0]
        self.assertFalse(result["automatable"])
        self.assertIn("__main__", result["reason"])

    def test_missing_statement_is_an_error(self):
        with self.assertRaises(LookupError):
            self.recommend([issue("x", "Assign", "long_statement", line_no=3)])


class HeldOutProgramTests(unittest.TestCase):
    def test_every_issue_gets_a_recommendation(self):
        from localization import localize_test_programs
        from train_model import train_model

        model, data, _, test = train_model()
        issues, _, _ = localize_test_programs(model, data, test)
        results = rec.recommend_refactorings(issues)
        summary = rec.summarize(results)
        self.assertEqual(
            summary["recommendations"],
            sum(len(i["detected_issues"]) for i in issues),
        )
        for result in results:
            for r in result["recommendations"]:
                self.assertIn(r["action"], rec.REFACTORINGS)
                self.assertGreaterEqual(r["severity"]["value"],
                                        r["severity"]["flagged_at"])
                self.assertEqual(r["automatable"], not r["reason"])


if __name__ == "__main__":
    unittest.main()
