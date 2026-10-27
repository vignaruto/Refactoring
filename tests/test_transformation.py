import ast
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import transformation as tf  # noqa: E402
from generate_dataset import statement_length  # noqa: E402


def target(line_no, statement_type, action):
    return {"line_no": line_no, "statement_type": statement_type, "action": action}


def run(source, name, args):
    namespace = {}
    exec(compile(source, "<test>", "exec"), namespace)
    try:
        return ("ok", namespace[name](*args))
    except Exception as error:  # noqa: BLE001
        return ("error", type(error).__name__)


class TransformTestCase(unittest.TestCase):
    def transform(self, source, *targets):
        source = textwrap.dedent(source)
        new, outcomes = tf.transform_source(source, list(targets))
        ast.parse(new)
        return source, new, outcomes

    def assert_same_behaviour(self, old, new, name, inputs):
        for args in inputs:
            with self.subTest(args=args):
                self.assertEqual(run(old, name, args), run(new, name, args))

    def assert_short(self, new, first_line, last_line):
        for line in new.splitlines()[first_line - 1:last_line]:
            if line.strip():
                self.assertLessEqual(statement_length(line.strip()), tf.LINE_LIMIT, line)


class DecomposeExpressionTests(TransformTestCase):
    INPUTS = [(1, 2, 3, 4, 5, 6), (0, -1, 2.5, 7, 3, 1), (9, 9, 9, 9, 9, 9)]

    def test_assignment_is_built_up_in_short_steps(self):
        old, new, outcomes = self.transform("""\
            def f(a, b, c, d, e, g):
                # keep this comment
                total = a * b + c * d + e * g + a * c + b * d + c * e + d * g
                return total
        """, target(3, "Assign", "DECOMPOSE_EXPRESSION"))
        self.assertEqual(outcomes[0]["status"], "applied")
        self.assertIn("# keep this comment", new)
        self.assert_short(new, 3, len(new.splitlines()) - 1)
        self.assert_same_behaviour(old, new, "f", self.INPUTS)

    def test_target_used_on_the_right_gets_a_new_name(self):
        old, new, _ = self.transform("""\
            def f(a, b, c, d, e, g):
                total = a
                total = total * 2 + b * c + d * e + g * a + total * b + c * d * e
                return total
        """, target(3, "Assign", "DECOMPOSE_EXPRESSION"))
        self.assertIn("partial", new)
        self.assert_same_behaviour(old, new, "f", self.INPUTS)

    def test_return_augassign_and_long_operand(self):
        old, new, outcomes = self.transform("""\
            def f(a, b, c, d, e, g):
                items = [a]
                items += [b] + [c] + [d] + [e] + [g] + [a, b] + [c, d] + [e, g]
                x = a - (b * c + d * e + g * a + b * d + c * e + d * g + a * a)
                return a * b + c * d + e * g + a * c + b * d + c * e + x + len(items)
        """, target(3, "AugAssign", "DECOMPOSE_EXPRESSION"),
            target(4, "Assign", "DECOMPOSE_EXPRESSION"),
            target(5, "Return", "DECOMPOSE_EXPRESSION"))
        self.assertEqual({o["status"] for o in outcomes}, {"applied"})
        self.assert_short(new, 3, len(new.splitlines()))
        self.assert_same_behaviour(old, new, "f", self.INPUTS)

    def test_class_body_is_not_applicable(self):
        _, _, outcomes = self.transform("""\
            class C:
                total = 1 * 2 + 3 * 4 + 5 * 6 + 7 * 8 + 9 * 10 + 11 * 12 + 13 * 14
        """, target(2, "Assign", "DECOMPOSE_EXPRESSION"))
        self.assertEqual(outcomes[0]["status"], "skipped")
        self.assertIn("class body", outcomes[0]["detail"])


class BooleanTests(TransformTestCase):
    INPUTS = [(None, 0), ({"v": 5, "f": True}, 3), ({"v": 1, "f": False}, 0),
              ({"v": 9, "f": True}, -2), ({"v": 9}, 1)]

    def test_short_circuit_is_kept(self):
        old, new, _ = self.transform("""\
            def f(x, n):
                ok = x is not None and x["v"] > 3 and x["f"] and n > 0 and x["v"] % 2 == 1
                return ok
        """, target(2, "Assign", "DECOMPOSE_BOOLEAN"))
        self.assert_short(new, 2, len(new.splitlines()) - 1)
        self.assert_same_behaviour(old, new, "f", self.INPUTS)

    def test_or_of_and_groups_with_guards(self):
        old, new, _ = self.transform("""\
            def f(x, n):
                if (x is not None and x["v"] > 3 and x["f"] is True) or (n > 0 and x is None and n % 2 == 1) or n == -2:
                    return "yes"
                return "no"
        """, target(2, "If", "EXTRACT_CONDITION"))
        self.assertIn("if not condition:", new)
        self.assert_short(new, 2, len(new.splitlines()) - 2)
        self.assert_same_behaviour(old, new, "f", self.INPUTS + [(None, 3), (None, -2)])


class ExtractConditionTests(TransformTestCase):
    def test_elif_condition_is_only_evaluated_after_earlier_branches(self):
        old, new, outcomes = self.transform("""\
            def f(x):
                if x is None:
                    return "none"
                elif x["a"] > 1 and x["b"] > 2 and x["c"] > 3:
                    return "big"
                elif x["a"] < 0:
                    return "negative"
                else:
                    return "other"
        """, target(4, "If", "EXTRACT_CONDITION"))
        self.assertEqual(outcomes[0]["status"], "applied")
        self.assertNotIn("elif x[\"a\"] > 1", new)
        inputs = [(None,), ({"a": 2, "b": 3, "c": 4},), ({"a": -1, "b": 0, "c": 0},),
                  ({"a": 0, "b": 0, "c": 0},), ({"a": 2, "b": 3},)]
        self.assert_same_behaviour(old, new, "f", inputs)

    def test_while_is_not_applicable(self):
        _, _, outcomes = self.transform("""\
            def f(a, b, c):
                while a and b and c:
                    a -= 1
                return a
        """, target(2, "While", "EXTRACT_CONDITION"))
        self.assertEqual(outcomes[0]["status"], "skipped")

    def test_names_avoid_existing_and_count_top_down(self):
        _, new, _ = self.transform("""\
            def f(a, b, c, condition):
                if a > 1 and b > 2 and c > 3:
                    return 1
                if a < 1 and b < 2 and c < 3:
                    return 2
                return condition
        """, target(2, "If", "EXTRACT_CONDITION"), target(4, "If", "EXTRACT_CONDITION"))
        lines = [line.strip() for line in new.splitlines()]
        self.assertIn("condition_2 = a > 1 and b > 2 and c > 3", lines)
        self.assertIn("condition_3 = a < 1 and b < 2 and c < 3", lines)
        self.assertIn("return condition", lines)


class FlattenTests(TransformTestCase):
    def test_independent_loops_become_one_product_loop(self):
        old, new, outcomes = self.transform("""\
            def f(n, m):
                out = []
                for i in range(n):
                    for j in range(m):
                        for k in range(2):
                            out.append((i, j, k))
                return out
        """, target(3, "For", "FLATTEN_WITH_PRODUCT"), target(4, "For", "FLATTEN_WITH_PRODUCT"))
        self.assertEqual([o["status"] for o in outcomes], ["applied", "covered"])
        self.assertIn("for i, j, k in itertools.product(range(n), range(m), range(2)):", new)
        self.assertEqual(new.count("import itertools"), 1)
        self.assert_same_behaviour(old, new, "f", [(0, 3), (2, 0), (3, 4)])

    def test_existing_product_import_is_reused(self):
        _, new, _ = self.transform("""\
            from itertools import product

            def f(xs, ys):
                total = 0
                for x in xs:
                    for y in ys:
                        total += x * y
                return total
        """, target(5, "For", "FLATTEN_WITH_PRODUCT"))
        self.assertIn("for x, y in product(xs, ys):", new)
        self.assertNotIn("import itertools", new)

    def test_unsafe_loops_are_not_flattened(self):
        cases = {
            "inner depends on outer": "for i in xs:\n        for j in range(i):\n            t += j",
            "break": "for i in xs:\n        for j in ys:\n            if j:\n                break",
            "inner iterable may raise": "for i in xs:\n        for j in range(len(ys[0])):\n            t += j",
            "inner iterable mutated": "for i in xs:\n        for j in ys:\n            ys.append(j)",
        }
        for name, loops in cases.items():
            with self.subTest(name):
                source = f"def f(xs, ys):\n    t = 0\n    {loops}\n    return t\n"
                _, _, outcomes = self.transform(source, target(3, "For", "FLATTEN_WITH_PRODUCT"))
                self.assertEqual(outcomes[0]["status"], "skipped")

    def test_loop_variable_used_after_loop_is_not_flattened(self):
        _, _, outcomes = self.transform("""\
            def f(xs, ys):
                for x in xs:
                    for y in ys:
                        pass
                return x
        """, target(2, "For", "FLATTEN_WITH_PRODUCT"))
        self.assertEqual(outcomes[0]["status"], "skipped")


class HeldOutProgramTests(unittest.TestCase):
    def test_refactored_programs_pass_their_self_tests(self):
        from localization import localize_test_programs, program_source
        from recommendation import recommend_refactorings
        from train_model import train_model

        model, data, _, test = train_model()
        issues, _, _ = localize_test_programs(model, data, test)
        programs = tf.transform_programs(recommend_refactorings(issues), program_source)
        self.assertGreater(len(programs), 100)
        with tempfile.TemporaryDirectory() as tmp:
            for pid, program in programs.items():
                path = Path(tmp) / program["filename"]
                path.write_text(program["transformed"])
                result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, f"{pid}: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
