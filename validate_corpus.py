
import ast
import csv
import hashlib
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "program_corpus" / "programs"
REPORT_FILE = BASE_DIR / "corpus_validation.csv"


def validate_corpus():

    if not CORPUS_DIR.is_dir():
        raise FileNotFoundError(
            f"Corpus directory not found: {CORPUS_DIR.resolve()}"
        )

    files = sorted(CORPUS_DIR.glob("*.py"))
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

    print("========== CORPUS VALIDATION ==========")
    print("Python files found:", len(files))
    print("Syntax-valid, non-empty files:", valid_count)
    print("Exact duplicate files:", duplicate_count)
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
