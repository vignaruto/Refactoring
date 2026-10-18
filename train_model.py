
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier


FEATURE_COLUMNS = [
    "statement_length",
    "operator_count",
    "operand_count",
    "expression_depth",
    "loop_depth",
    "condition_count",
    "logical_operator_count"
]

LABEL_COLUMNS = [
    "long_statement",
    "nested_loop",
    "complex_conditional"
]


def train_model(dataset_path="dataset.csv"):
    """Load the dataset, train one multi-output model, and return it."""

    data = pd.read_csv(dataset_path)

    X = data[FEATURE_COLUMNS]
    Y = data[LABEL_COLUMNS]

    base_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model = MultiOutputClassifier(base_model)
    model.fit(X, Y)

    return model, data


if __name__ == "__main__":
    model, data = train_model()

    print("Model training completed.")
    print("Dataset rows:", len(data))
    print("Features:", FEATURE_COLUMNS)
    print("Labels:", LABEL_COLUMNS)
