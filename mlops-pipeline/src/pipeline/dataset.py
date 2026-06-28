from pathlib import Path

import pandas as pd

from pipeline.errors import InvalidDatasetError
from pipeline.models import Dataset


def load_dataset(path: Path, label_column: str) -> Dataset:
    if not path.is_file():
        raise InvalidDatasetError(f"dataset not found: {path}")

    frame = pd.read_csv(path)
    if label_column not in frame.columns:
        raise InvalidDatasetError(f"missing label column: {label_column}")
    if frame.empty:
        raise InvalidDatasetError("dataset is empty")

    labels = [int(value) for value in frame[label_column].tolist()]
    feature_rows = frame.drop(columns=[label_column]).to_numpy().tolist()
    features = [[float(value) for value in row] for row in feature_rows]
    return Dataset(features=features, labels=labels)
