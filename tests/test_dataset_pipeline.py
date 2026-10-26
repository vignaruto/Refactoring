import ast
import csv
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import generate_dataset as gd  # noqa: E402


def extract(source):
    source = textwrap.dedent(source)
    return gd.extract_statements(
        ast.parse(source), source.splitlines(keepends=True)
    )


def by_code(records):
    return {record["code"]: record for record in records}


class ComplexConditionalTests(unittest.TestCase):
    CASES = [
        # (header, atomic conditions, expected label)
        ("if a or b:", 2, 0),
        ("if (a or b) and c:", 3, 1),
        ("if a and b and c:", 3, 1),
        ("if 0 <= x < n:", 2, 0),
        ("if x is None and y is None:", 2, 0),
        ("if (a and (b or not c)) or d < e < f:", 5, 1),
        ("if not (a and b):", 2, 0),
        ("if 0 <= x < n and ok:", 3, 1),
        ("if any(a and b and c for a, b, c in rows):", 1, 0),
        ("while lo <= hi and not found and steps < limit:", 3, 1),
        ("while i < n and not done:", 2, 0),
    ]

    def test_cases(self):
        for header, atoms, label in self.CASES:
            with self.subTest(header=header):
                node = ast.parse(header + "\n    pass\n").body[0]
                self.assertEqual(gd.count_atomic_conditions(node.test), atoms)

                record = extract(header + "\n    pass\n")[0]
                self.assertEqual(record["code"], header)
                self.assertEqual(record["complex_conditional"], label)

    def test_only_if_and_while_are_labeled(self):
        records = extract("""
            flag = a and b and c
            for item in (x for x in xs if p and q and r):
                pass
        """)
        self.assertEqual(
            [record["complex_conditional"] for record in records], [0, 0]
        )


class LengthAndScaffoldTests(unittest.TestCase):
    def test_multiline_length_matches_one_line_form(self):
        one_line = 'x = {"a": 1, "b": 2}'
        records = extract("""
            x = {
                "a": 1,
                "b": 2
            }
            y = 1 + \\
                2
        """)
        self.assertEqual(records[0]["statement_length"], len(one_line))
        self.assertEqual(records[1]["statement_length"], len("y = 1 + 2"))

    def test_main_guard_rows_are_flagged(self):
        records = extract("""
            def f():
                return 1

            if __name__ == "__main__":
                value = f()
                assert value == 1
        """)
        self.assertEqual(
            [record["in_main_guard"] for record in records], [0, 1, 1]
        )


class DocstringTests(unittest.TestCase):
    SOURCE = '''
        """Module docstring that is definitely longer than sixty characters in total."""

        class Box:
            """Class docstring that is definitely longer than sixty characters in total."""

            def size(self):
                """Function docstring that is definitely longer than sixty characters."""
                "A standalone string expression that is not a docstring at all, really."
                if self:
                    "First statement of an if body, which is not a docstring either."
                return 1
    '''

    def test_only_genuine_docstrings_are_excluded(self):
        records = extract(self.SOURCE)
        codes = [record["code"] for record in records]

        self.assertFalse(any("docstring that" in code for code in codes))

        standalone = [r for r in records if "not a docstring" in r["code"]]
        self.assertEqual(len(standalone), 2)
        for record in standalone:
            self.assertEqual(record["statement_type"], "Expr")
            self.assertEqual(record["long_statement"], 1)

    def test_docstring_count(self):
        source = textwrap.dedent(self.SOURCE)
        self.assertEqual(gd.count_docstrings(ast.parse(source)), 3)


class RecordPolicyTests(unittest.TestCase):
    SOURCE = """
        def scale(matrix, factor):
            result = []
            for row in matrix:  # outer loop
                for val in row:
                    if (
                        val > 0
                        and factor > 0
                    ):  # positive
                        result.append(val * factor)
                    elif val == 0:
                        result.append(0)
            else:
                done = True
            while result:
                result.pop()
            return result

        for i in range(3):
            def helper():
                return i
            total = i + 1
    """

    def setUp(self):
        self.records = extract(self.SOURCE)
        self.codes = by_code(self.records)

    def test_headers_are_not_bodies(self):
        self.assertIn("for row in matrix:", self.codes)
        self.assertIn("for val in row:", self.codes)
        self.assertIn("elif val == 0:", self.codes)
        self.assertIn("if (\n                val > 0\n"
                      "                and factor > 0\n            ):",
                      self.codes)

    def test_ids_are_sequential_in_source_order(self):
        self.assertEqual(
            [record["statement_id"] for record in self.records],
            list(range(1, len(self.records) + 1)),
        )
        starts = [record["line_no"] for record in self.records]
        self.assertEqual(starts, sorted(starts))

    def test_no_overlapping_line_ranges(self):
        for previous, current in zip(self.records, self.records[1:]):
            self.assertGreater(current["line_no"], previous["end_line"])

    def test_nested_loop_context_is_kept(self):
        outer = self.codes["for row in matrix:"]
        inner = self.codes["for val in row:"]
        self.assertEqual(outer["nested_loop"], 1)
        self.assertEqual(outer["loop_depth"], 2)
        self.assertEqual(inner["nested_loop"], 0)
        self.assertEqual(inner["parent_statement_id"], outer["statement_id"])
        self.assertEqual(inner["enclosing_loop_depth"], 1)

    def test_header_features_exclude_body(self):
        outer = self.codes["for row in matrix:"]
        self.assertEqual(outer["operator_count"], 0)
        self.assertEqual(outer["condition_count"], 0)
        self.assertEqual(outer["operand_count"], 2)

    def test_parent_and_enclosing_loop_depth(self):
        append = self.codes["result.append(val * factor)"]
        guard = next(r for r in self.records if r["code"].startswith("if ("))
        self.assertEqual(append["parent_statement_id"], guard["statement_id"])
        self.assertEqual(append["enclosing_loop_depth"], 2)

        elif_record = self.codes["elif val == 0:"]
        self.assertEqual(elif_record["parent_statement_id"],
                         guard["statement_id"])

        loop_else = self.codes["done = True"]
        self.assertEqual(loop_else["parent_statement_id"],
                         self.codes["for row in matrix:"]["statement_id"])
        self.assertEqual(loop_else["enclosing_loop_depth"], 0)

        self.assertEqual(self.codes["result = []"]["parent_statement_id"], "")

    def test_function_scope_resets_context(self):
        inner_return = self.codes["return i"]
        self.assertEqual(inner_return["parent_statement_id"], "")
        self.assertEqual(inner_return["enclosing_loop_depth"], 0)

        total = self.codes["total = i + 1"]
        self.assertEqual(total["enclosing_loop_depth"], 1)
        self.assertEqual(total["parent_statement_id"],
                         self.codes["for i in range(3):"]["statement_id"])

    def test_trailing_comments_are_not_code(self):
        self.assertNotIn("#", "".join(r["code"] for r in self.records))

    def test_overlap_check_rejects_overlap(self):
        with self.assertRaises(ValueError):
            gd.check_record_spans([((1, 0), (3, 0)), ((2, 4), (2, 9))])


class ProjectCopyTestCase(unittest.TestCase):
    """Runs scripts in a temporary copy of the project."""

    SCRIPTS = [
        "generate_dataset.py",
        "audit_dataset.py",
        "validate_corpus.py",
        "build_corpus.py",
    ]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=PROJECT_DIR)
        self.copy = Path(self._tmp.name) / "project"
        self.copy.mkdir()
        for script in self.SCRIPTS:
            shutil.copy2(PROJECT_DIR / script, self.copy / script)
        shutil.copytree(
            PROJECT_DIR / "program_corpus", self.copy / "program_corpus"
        )
        self.outside_cwd = Path(self._tmp.name) / "elsewhere"
        self.outside_cwd.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def run_script(self, name):
        return subprocess.run(
            [sys.executable, str(self.copy / name)],
            cwd=self.outside_cwd,
            capture_output=True,
            text=True,
        )


class PathResolutionTests(ProjectCopyTestCase):
    def test_scripts_run_from_outside_project_root(self):
        for name in [
            "validate_corpus.py",
            "generate_dataset.py",
            "audit_dataset.py",
        ]:
            with self.subTest(script=name):
                result = self.run_script(name)
                self.assertEqual(result.returncode, 0, result.stderr)

        for output in [
            "corpus_validation.csv",
            "dataset.csv",
        ]:
            self.assertTrue((self.copy / output).is_file(), output)
            self.assertFalse((self.outside_cwd / output).exists(), output)


class UniquenessCheckTests(unittest.TestCase):
    """check_uniqueness only reads the real corpus; nothing is written."""

    @classmethod
    def setUpClass(cls):
        import build_corpus
        cls.bc = build_corpus
        cls.manifest = build_corpus.read_existing_manifest()
        cls.programs = build_corpus.PROGRAMS_DIR

    def problems_for(self, task, code):
        problems, _ = self.bc.check_uniqueness(
            [("P9999", task, code)], self.manifest
        )
        return problems

    def test_renamed_copy_is_rejected(self):
        code = (self.programs / "P0265.py").read_text()
        for old, new in [("insertion_sort", "shift_sort"),
                         ("items", "seq"), ("current", "key"),
                         ("position", "pos"), ("values", "data")]:
            code = code.replace(old, new)
        problems = self.problems_for("A brand new task", code)
        self.assertTrue(any("near-identical to P0265" in p for p in problems))

    def test_reformatted_copy_is_rejected(self):
        code = "# reformatted\n" + (self.programs / "P0251.py").read_text()
        code = code.replace("def modular_power", "def  modular_power")
        problems = self.problems_for("A brand new task", code)
        self.assertTrue(any("same code as P0251" in p for p in problems))

    def test_repeated_task_and_function_name_are_rejected(self):
        code = "def binary_search(xs, x):\n    return x in xs\n"
        problems = self.problems_for("Binary search!", code)
        self.assertTrue(any("repeats the task of P0006" in p for p in problems))
        self.assertTrue(any("['binary_search']" in p for p in problems))

    def test_distinct_program_passes(self):
        code = (
            "def luhn_checksum_digit(payload: str) -> int:\n"
            "    total = 0\n"
            "    for index, char in enumerate(reversed(payload)):\n"
            "        digit = int(char) * (2 if index % 2 == 0 else 1)\n"
            "        total += digit - 9 if digit > 9 else digit\n"
            "    return (10 - total % 10) % 10\n"
        )
        self.assertEqual(
            self.problems_for("Compute a Luhn check digit", code), []
        )

    def test_existing_corpus_has_unique_ids_tasks_and_names(self):
        tasks = [
            self.bc.normalized_task(row["task_description"])
            for row in self.manifest.values()
        ]
        self.assertEqual(len(tasks), len(set(tasks)))

        names = []
        for path in sorted(self.programs.glob("*.py")):
            names.extend(self.bc.program_profile(path.read_text())["functions"])
        self.assertEqual(len(names), len(set(names)))


class ArchitectureFitTests(unittest.TestCase):
    CODE = (
        "def clamp_total(values: list[int], cap: int) -> int:\n"
        "    total = sum(values)\n"
        "    return min(total, cap)\n"
        "\n"
        "if __name__ == \"__main__\":\n"
        "    assert clamp_total([1, 2], 2) == 2\n"
    )

    def setUp(self):
        import build_corpus
        self.bc = build_corpus

    def problems_for(self, code, category="None",
                     domain="Numerical Computation"):
        row = {"domain": domain, "intended_category": category}
        return self.bc.check_architecture_fit("P9999", row, code)

    def test_fitting_program_passes(self):
        self.assertEqual(self.problems_for(self.CODE), [])

    def test_category_must_match_rule_labels(self):
        problems = self.problems_for(self.CODE, "Nested loop only")
        self.assertTrue(any("rule labels are none" in p for p in problems))

    def test_pipeline_constraints(self):
        code = self.CODE.replace(
            "    total = sum(values)\n",
            "    _temp1 = 0; total = sum(values)\n",
        ).replace("== 2", "== 3")
        problems = self.problems_for(code, domain="Matrix Operations")
        for expected in ["unknown domain", "several statements",
                         "reserved name", "self-test failed"]:
            self.assertTrue(any(expected in p for p in problems), expected)

    def test_self_test_is_required(self):
        code = self.CODE.split("if __name__")[0]
        problems = self.problems_for(code)
        self.assertTrue(any("no assert-based" in p for p in problems))

    def test_whole_corpus_fits(self):
        manifest = self.bc.read_existing_manifest()
        for pid, row in manifest.items():
            code = (self.bc.PROGRAMS_DIR / row["filename"]).read_text()
            with self.subTest(pid=pid):
                self.assertEqual(
                    self.bc.check_architecture_fit(
                        pid, row, code, allow_scaffold_issues=True
                    ),
                    [],
                )

    def test_issues_in_main_block_are_rejected(self):
        code = self.CODE.replace(
            "    assert clamp_total([1, 2], 2) == 2\n",
            "    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]\n"
            "    assert clamp_total(numbers, 2) == 2\n",
        )
        problems = self.problems_for(code)
        self.assertTrue(any("__main__ block" in p for p in problems))


class SimilarityGroupTests(unittest.TestCase):
    def setUp(self):
        import validate_corpus
        self.similarity_groups = validate_corpus.similarity_groups
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, pid, code):
        path = self.dir / f"{pid}.py"
        path.write_text(code, encoding="utf-8")
        return path

    def test_renamed_copies_share_the_smallest_id(self):
        original = (PROJECT_DIR / "program_corpus" / "programs" / "P0265.py")
        code = original.read_text()
        renamed = code.replace("insertion_sort", "shift_sort")
        renamed = renamed.replace("items", "seq").replace("values", "data")
        files = [
            self.write("P0002", renamed),
            self.write("P0001", code),
            self.write("P0003", "def f(x):\n    return x\n"),
            self.write("P0004", "def broken(:\n"),
        ]
        groups = self.similarity_groups(files)
        self.assertEqual(groups["P0001"], "P0001")
        self.assertEqual(groups["P0002"], "P0001")
        self.assertEqual(groups["P0003"], "P0003")
        self.assertEqual(groups["P0004"], "P0004")

    def test_corpus_groups_are_stable(self):
        corpus = PROJECT_DIR / "program_corpus" / "programs"
        groups = self.similarity_groups(sorted(corpus.glob("*.py")))
        self.assertEqual(groups["P0231"], "P0131")
        self.assertEqual(groups["P0246"], "P0196")
        self.assertEqual(groups["P0301"], "P0301")
        for pid, group in groups.items():
            self.assertLessEqual(group, pid)
            self.assertEqual(groups[group], group)


class ManifestSafetyTests(ProjectCopyTestCase):
    def manifest_ids(self):
        with (self.copy / "program_corpus" / "manifest.csv").open(
            newline="", encoding="utf-8-sig"
        ) as f:
            return [row["program_id"] for row in csv.DictReader(f)]

    def snapshot(self):
        corpus = self.copy / "program_corpus"
        return {
            path.relative_to(corpus): path.read_bytes()
            for path in sorted(corpus.rglob("*"))
            if path.is_file()
        }

    def test_rerun_is_a_no_op(self):
        before = self.snapshot()
        result = self.run_script("build_corpus.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Appended 0 new manifest rows", result.stdout)
        self.assertEqual(self.snapshot(), before)

        ids = self.manifest_ids()
        self.assertEqual(len(ids), len(set(ids)))

    def test_differing_program_file_stops_without_writing(self):
        program = self.copy / "program_corpus" / "programs" / "P0651.py"
        program.write_text(program.read_text() + "\n# edited\n")
        before = self.snapshot()

        result = self.run_script("build_corpus.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("P0651.py exists with different content", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_conflicting_manifest_metadata_stops_without_writing(self):
        manifest = self.copy / "program_corpus" / "manifest.csv"
        with manifest.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)
        for row in rows:
            if row["program_id"] == "P0652":
                row["intended_category"] = "Long statement only"
        with manifest.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        before = self.snapshot()

        result = self.run_script("build_corpus.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("P0652 is already in the manifest", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_malformed_manifest_row_stops_without_writing(self):
        manifest = self.copy / "program_corpus" / "manifest.csv"
        with manifest.open("a", encoding="utf-8") as f:
            f.write("P9999,P9999.py,too,few\n")
        before = self.snapshot()

        result = self.run_script("build_corpus.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Malformed manifest row", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_missing_rows_and_files_are_added_once(self):
        removed = ["P0699", "P0700"]
        manifest = self.copy / "program_corpus" / "manifest.csv"
        lines = manifest.read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [
            line for line in lines
            if not any(line.startswith(pid + ",") for pid in removed)
        ]
        manifest.write_text("".join(kept), encoding="utf-8")
        for pid in removed:
            (self.copy / "program_corpus" / "programs" / f"{pid}.py").unlink()

        for _ in range(2):
            result = self.run_script("build_corpus.py")
            self.assertEqual(result.returncode, 0, result.stderr)

        ids = self.manifest_ids()
        self.assertEqual(len(ids), len(set(ids)))
        for pid in removed:
            self.assertEqual(ids.count(pid), 1)
            self.assertTrue(
                (self.copy / "program_corpus" / "programs" / f"{pid}.py")
                .is_file()
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
