
import ast
import csv
import difflib
import hashlib
from pathlib import Path

from build_corpus import STRUCTURAL_SIMILARITY_LIMIT, program_profile


BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "program_corpus" / "programs"
REPORT_FILE = BASE_DIR / "corpus_validation.csv"


def similarity_groups(files):
    """
    Map each program_id to its near-duplicate group.

    Programs linked by a chain of pairs whose AST node-type sequences are
    at least STRUCTURAL_SIMILARITY_LIMIT similar share a group, named after
    its smallest program_id; every other program is its own group. Train
    and test splits must keep each group on one side, otherwise renamed
    copies of a training program leak into the test set.
    """
    shapes = {}
    for path in files:
        try:
            profile = program_profile(path.read_text(encoding="utf-8"))
            shapes[path.stem] = profile["shape"]
        except SyntaxError:
            shapes[path.stem] = None

    ids = sorted(shapes)
    parent = {pid: pid for pid in ids}

    def root(pid):
        while parent[pid] != pid:
            pid = parent[pid]
        return pid

    limit = STRUCTURAL_SIMILARITY_LIMIT
    for index, first in enumerate(ids):
        if shapes[first] is None:
            continue
        for second in ids[index + 1:]:
            if shapes[second] is None:
                continue
            matcher = difflib.SequenceMatcher(
                None, shapes[first], shapes[second], autojunk=False
            )
            if (
                matcher.real_quick_ratio() >= limit
                and matcher.quick_ratio() >= limit
                and matcher.ratio() >= limit
            ):
                a, b = root(first), root(second)
                parent[max(a, b)] = min(a, b)

    return {pid: root(pid) for pid in ids}


def validate_corpus():

    if not CORPUS_DIR.is_dir():
        raise FileNotFoundError(
            f"Corpus directory not found: {CORPUS_DIR.resolve()}"
        )

    files = sorted(CORPUS_DIR.glob("*.py"))
    groups = similarity_groups(files)
    results = []
    seen_hashes = {}

    for path in files:

        source = path.read_text(encoding="utf-8")
        source_hash = hashlib.sha256(
            source.encode("utf-8")
        ).hexdigest()

        syntax_valid = True
        syntax_error = ""

        try:
            tree = ast.parse(source)
            has_function = any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                for node in ast.walk(tree)
            )
        except SyntaxError as error:
            syntax_valid = False
            syntax_error = str(error)
            has_function = False

        duplicate_of = seen_hashes.get(source_hash, "")

        if not duplicate_of:
            seen_hashes[source_hash] = path.name

        results.append({
            "program_id": path.stem,
            "filename": path.name,
            "characters": len(source),
            "syntax_valid": syntax_valid,
            "has_function": has_function,
            "empty_file": not source.strip(),
            "sha256": source_hash,
            "duplicate_of": duplicate_of,
            "similarity_group": groups[path.stem],
            "syntax_error": syntax_error
        })

    fields = [
        "program_id",
        "filename",
        "characters",
        "syntax_valid",
        "has_function",
        "empty_file",
        "sha256",
        "duplicate_of",
        "similarity_group",
        "syntax_error"
    ]

    with REPORT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    valid_count = sum(
        row["syntax_valid"] and not row["empty_file"]
        for row in results
    )

    duplicate_count = sum(
        bool(row["duplicate_of"]) for row in results
    )

    members = {}
    for pid, group in groups.items():
        members.setdefault(group, []).append(pid)
    shared_groups = [ids for ids in members.values() if len(ids) > 1]

    print("========== CORPUS VALIDATION ==========")
    print("Python files found:", len(files))
    print("Syntax-valid, non-empty files:", valid_count)
    print("Exact duplicate files:", duplicate_count)
    print(
        f"Near-duplicate groups (structural similarity >= "
        f"{STRUCTURAL_SIMILARITY_LIMIT}): {len(shared_groups)} groups "
        f"covering {sum(map(len, shared_groups))} programs"
    )
    for ids in shared_groups:
        print("  ", ", ".join(ids))
    print("Report saved to:", REPORT_FILE)

    print("\nFiles requiring attention:")

    for row in results:
        if (
            not row["syntax_valid"]
            or row["empty_file"]
            or row["duplicate_of"]
            or not row["has_function"]
        ):
            print(row["filename"], row)


if __name__ == "__main__":
    validate_corpus()
