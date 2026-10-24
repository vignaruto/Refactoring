
import pandas as pd

DATASET_FILE = "dataset.csv"

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

print("\nAudit completed.")
