
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "dataset.csv"

df = pd.read_csv(DATASET_FILE)

labels = [
    "long_statement",
    "nested_loop",
    "complex_conditional",
]

print("=" * 65)
print("S7 DATASET LABEL AUDIT")
print("=" * 65)

print("\n1. Dataset dimensions")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Unique programs:", df["program_id"].nunique())

print("\n2. Missing values in important columns")
important_columns = [
    "program_id",
    "filename",
    "statement_id",
    "statement_type",
    "line_no",
    "code",
] + labels

for column in important_columns:
    if column in df.columns:
        print(f"{column}: {df[column].isna().sum()}")

print("\n3. Label distribution")
for label in labels:
    print(f"\n{label}")
    print(df[label].value_counts(dropna=False).sort_index())

print("\n4. Positive examples for manual inspection")

for label in labels:
    positives = df[df[label] == 1]

    print("\n" + "-" * 65)
    print(f"LABEL: {label}")
    print("-" * 65)

    if positives.empty:
        print("No positive examples.")
        continue

    # Sample across the corpus rather than taking
    # only the first few records.
    sample = positives.sample(
        n=min(10, len(positives)),
        random_state=42,
    )

    for _, row in sample.iterrows():
        print(
            f"\nProgram: {row['program_id']} | "
            f"Lines: {row['line_no']}-{row['end_line']} | "
            f"Type: {row['statement_type']}"
        )
        print("Code:")
        print(row["code"])
        print(
            "Features:",
            {
                "statement_length": row["statement_length"],
                "operator_count": row["operator_count"],
                "expression_depth": row["expression_depth"],
                "loop_depth": row["loop_depth"],
                "condition_count": row["condition_count"],
                "logical_operator_count":
                    row["logical_operator_count"],
            },
        )

print("\n5. Potential duplicate statement records")

duplicate_mask = df.duplicated(
    subset=["program_id", "line_no", "end_line", "statement_type"],
    keep=False,
)

print("Records sharing program, line span and type:",
      int(duplicate_mask.sum()))

if duplicate_mask.any():
    print(
        df.loc[
            duplicate_mask,
            [
                "program_id",
                "line_no",
                "end_line",
                "statement_type",
                "code",
            ],
        ].head(20).to_string(index=False)
    )

print("\n6. Overlapping source-line ranges within a program")

overlapping_pairs = 0
for _, group in df.sort_values(["program_id", "line_no"]).groupby("program_id"):
    latest_end = 0
    for start, end in zip(group["line_no"], group["end_line"]):
        if start <= latest_end:
            overlapping_pairs += 1
        latest_end = max(latest_end, end)

print("Records starting inside an earlier record's line range:",
      overlapping_pairs)

print("\n7. Statement-ID and parent consistency")

print("Duplicate (program_id, statement_id):",
      int(df.duplicated(subset=["program_id", "statement_id"]).sum()))

if "parent_statement_id" in df.columns:
    ids = set(zip(df["program_id"], df["statement_id"]))
    with_parent = df[df["parent_statement_id"].notna()]
    dangling = sum(
        (program, int(parent)) not in ids or int(parent) >= statement
        for program, parent, statement in zip(
            with_parent["program_id"],
            with_parent["parent_statement_id"],
            with_parent["statement_id"],
        )
    )
    print("Records with a parent:", len(with_parent))
    print("Parents missing or not earlier in the program:", dangling)
else:
    print("parent_statement_id column not present.")

print("\nAudit completed.")
