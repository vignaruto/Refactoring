
import pandas as pd

INPUT_FILE = "dataset.csv"
OUTPUT_FILE = "label_review_sample.csv"

LABELS = [
    "long_statement",
    "nested_loop",
    "complex_conditional",
]

SAMPLE_SIZE = 20
RANDOM_STATE = 42

df = pd.read_csv(INPUT_FILE)

# Collect positive and negative examples for every issue.
sample_indices = set()

for label in LABELS:
    for value in [1, 0]:
        group = df[df[label] == value]

        n = min(SAMPLE_SIZE, len(group))

        if n:
            sampled = group.sample(
                n=n,
                random_state=RANDOM_STATE + value,
            )
            sample_indices.update(sampled.index.tolist())

review = df.loc[sorted(sample_indices)].copy()

# Add blank fields for independent manual review.
for label in LABELS:
    review[f"reviewed_{label}"] = ""

review["review_notes"] = ""

# Put identifiers and code first for easier inspection.
first_columns = [
    "program_id",
    "filename",
    "statement_id",
    "statement_type",
    "line_no",
    "end_line",
    "code",
]

review_columns = [
    f"reviewed_{label}" for label in LABELS
] + ["review_notes"]

other_columns = [
    column
    for column in review.columns
    if column not in first_columns + review_columns
]

review = review[
    first_columns + review_columns + other_columns
]

review.to_csv(OUTPUT_FILE, index=False)

print("Label-review sample created.")
print("Unique statements:", len(review))
print("Saved to:", OUTPUT_FILE)

print("\nOriginal labels represented in sample:")
for label in LABELS:
    print(f"\n{label}:")
    print(review[label].value_counts().sort_index())
