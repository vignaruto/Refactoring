import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import localization as loc  # noqa: E402
from train_model import train_model  # noqa: E402


def rows(*records):
    base = {"program_id": "P1", "filename": "P1.py", "in_main_guard": 0,
            "long_statement": 0, "nested_loop": 0, "complex_conditional": 0}
    return pd.DataFrame([{**base, **record} for record in records])


class LocalizeIssuesTests(unittest.TestCase):
    def test_type_mismatched_predictions_are_dropped(self):
        data = rows(
            {"statement_id": 1, "line_no": 2, "end_line": 2,
             "statement_type": "If", "code": "if a:"},
            {"statement_id": 2, "line_no": 3, "end_line": 3,
             "statement_type": "Return", "code": "return x"},
        )
        predictions = [[1, 1, 1], [1, 1, 1]]
        issues, dropped = loc.localize_issues(data, predictions)
        self.assertEqual(
            [(i["line_no"], i["detected_issues"]) for i in issues],
            [(2, ["complex_conditional"]), (3, ["long_statement"])],
        )
        self.assertEqual(len(dropped), 4)

    def test_issue_keeps_program_and_span(self):
        data = rows({"statement_id": 1, "line_no": 4, "end_line": 6,
                     "statement_type": "While", "code": "while x:"})
        issues, _ = loc.localize_issues(data, [[0, 1, 1]], [[0.0, 0.9, 0.8]])
        issue = issues[0]
        self.assertEqual((issue["program_id"], issue["line_no"], issue["end_line"]),
                         ("P1", 4, 6))
        self.assertEqual(issue["confidence"],
                         {"nested_loop": 0.9, "complex_conditional": 0.8})


class VerifyLocationsTests(unittest.TestCase):
    SOURCE = "def f(a):\n    x = a + 1\n    return x\n"

    def issue(self, line_no, code):
        return {"program_id": "P1", "filename": "P1.py", "line_no": line_no,
                "end_line": line_no, "code": code}

    def test_correct_span_passes_and_wrong_span_fails(self):
        source_for = lambda issue: self.SOURCE  # noqa: E731
        self.assertEqual(loc.verify_locations([self.issue(2, "x = a + 1")], source_for), [])
        self.assertEqual(
            len(loc.verify_locations([self.issue(3, "x = a + 1")], source_for)), 1
        )


class EvaluateLocalizationTests(unittest.TestCase):
    def test_counts_hits_misses_and_false_alarms(self):
        data = rows(
            {"statement_id": 1, "line_no": 1, "code": "a", "long_statement": 1},
            {"statement_id": 2, "line_no": 2, "code": "b", "long_statement": 1},
            {"statement_id": 3, "line_no": 3, "code": "c"},
        )
        issues = [
            {"program_id": "P1", "statement_id": 1, "detected_issues": ["long_statement"]},
            {"program_id": "P1", "statement_id": 3, "detected_issues": ["long_statement"]},
        ]
        result = loc.evaluate_localization(data, issues)
        m = result["statement_level"]["long_statement"]
        self.assertEqual((m["tp"], m["fp"], m["fn"]), (1, 1, 1))
        self.assertEqual(result["programs_localized_exactly"], 0)
        self.assertEqual(sorted(e["kind"] for e in result["errors"]),
                         ["false_alarm", "missed"])


class EndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.data, _, cls.test = train_model()

    def test_held_out_programs(self):
        issues, _, evaluation = loc.localize_test_programs(
            self.model, self.data, self.test
        )
        self.assertEqual(evaluation["programs"], 160)
        self.assertTrue(issues)
        for m in evaluation["statement_level"].values():
            self.assertGreaterEqual(m["f1"], 0.95)

    def test_localize_new_file(self):
        source = textwrap.dedent("""\
            def score(a, b, c, d):
                total = a * b + c * d + a * c + b * d + a * d + b * c + a + b
                if a > b and b > c and c > d:
                    total += 1
                for i in range(a):
                    for j in range(b):
                        total += i * j
                return total
        """)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text(source)
            issues, _ = loc.localize_file(self.model, path)
        self.assertEqual(
            [(i["line_no"], i["detected_issues"]) for i in issues],
            [(2, ["long_statement"]), (3, ["complex_conditional"]),
             (5, ["nested_loop"])],
        )


if __name__ == "__main__":
    unittest.main()
