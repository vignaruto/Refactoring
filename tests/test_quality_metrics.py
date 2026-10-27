import sys
import textwrap
import unittest
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import quality_metrics as qm  # noqa: E402

BEFORE = textwrap.dedent("""\
    def f(xs, ys, a, b, c):
        total = 0
        for x in xs:
            for y in ys:
                total += x * y
        if a > 1 and b > 2 and c > 3:
            total = total * a + total * b + total * c + a * b * c + a + b + c
        return total


    if __name__ == "__main__":
        assert f([1], [2], 0, 0, 0) == 2 and f([], [], 2, 3, 4) == 0 and True
""")

AFTER = textwrap.dedent("""\
    import itertools

    def f(xs, ys, a, b, c):
        total = 0
        for x, y in itertools.product(xs, ys):
            total += x * y
        condition = a > 1 and b > 2 and c > 3
        if condition:
            partial = total * a + total * b + total * c
            total = partial + a * b * c + a + b + c
        return total


    if __name__ == "__main__":
        assert f([1], [2], 0, 0, 0) == 2 and f([], [], 2, 3, 4) == 0 and True
""")


class MetricTests(unittest.TestCase):
    def test_main_guard_is_excluded(self):
        self.assertNotIn("__main__", qm.program_code(BEFORE))
        self.assertEqual(qm.program_code("x = 1\n"), "x = 1\n")

    def test_metrics_before_and_after(self):
        before, after = qm.calculate_metrics(BEFORE), qm.calculate_metrics(AFTER)
        self.assertEqual(set(before), set(qm.METRICS))
        self.assertEqual((before["long_statements"], before["nested_loops"],
                          before["complex_conditionals"]), (1, 1, 1))
        self.assertEqual((after["long_statements"], after["nested_loops"],
                          after["complex_conditionals"]), (0, 0, 0))
        self.assertEqual((before["max_condition_atoms"], after["max_condition_atoms"]), (3, 1))
        self.assertEqual((before["max_nesting_depth"], after["max_nesting_depth"]), (2, 1))
        self.assertLess(after["cognitive_complexity"], before["cognitive_complexity"])
        self.assertLessEqual(after["max_statement_length"], 60)

    def test_issue_changes(self):
        changes = qm.issue_changes(BEFORE, AFTER)
        for label in qm.ISSUES:
            self.assertEqual(changes[label],
                             {"before": 1, "after": 0, "resolved": 1, "introduced": 0})
        self.assertEqual(qm.issue_changes(BEFORE, BEFORE)["long_statement"]["resolved"], 0)


class StatisticsTests(unittest.TestCase):
    def test_direction_of_better(self):
        rows = []
        for i in range(8):
            row = {"program_id": f"P{i}", "changed": True}
            for metric, (_, higher_is_better) in qm.METRICS.items():
                row[f"{metric}_before"] = 10.0 + i
                row[f"{metric}_after"] = 12.0 + i
            rows.append(row)
        stats = qm.metric_statistics(pd.DataFrame(rows))
        self.assertEqual(stats["maintainability_index"]["programs_better"], 8)
        self.assertEqual(stats["logical_lines"]["programs_worse"], 8)
        self.assertLess(stats["logical_lines"]["wilcoxon_p_changed_programs"], 0.05)


if __name__ == "__main__":
    unittest.main()
