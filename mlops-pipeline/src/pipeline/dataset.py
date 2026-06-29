import hashlib
import json
from collections import Counter
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandera import errors as pa_errors

from pipeline.errors import InvalidDatasetError
from pipeline.models import Dataset

_MIN_PER_CLASS = 2


def _validate_frame(frame: pd.DataFrame, label_column: str) -> pd.DataFrame:
    if label_column not in frame.columns:
        raise InvalidDatasetError(f"missing label column: {label_column}")
    if frame.empty:
        raise InvalidDatasetError("dataset is empty")

    feature_columns = [column for column in frame.columns if column != label_column]
    if not feature_columns:
        raise InvalidDatasetError("dataset has no feature columns")

    columns: dict[str, pa.Column] = {
        column: pa.Column(float, nullable=False, coerce=True) for column in feature_columns
    }
    columns[label_column] = pa.Column(int, nullable=False, coerce=True)
    schema = pa.DataFrameSchema(columns)
    try:
        return schema.validate(frame, lazy=True)
    except (pa_errors.SchemaError, pa_errors.SchemaErrors) as exc:
        raise InvalidDatasetError("schema validation failed") from exc


def _validate_class_balance(labels: list[int]) -> None:
    counts = Counter(labels)
    if len(counts) < 2:
        raise InvalidDatasetError("dataset must contain at least 2 classes")
    underfilled = {label: count for label, count in counts.items() if count < _MIN_PER_CLASS}
    if underfilled:
        raise InvalidDatasetError(f"each class needs >= {_MIN_PER_CLASS} samples: {underfilled}")


def load_dataset(path: Path, label_column: str) -> Dataset:
    if not path.is_file():
        raise InvalidDatasetError(f"dataset not found: {path}")

    frame = _validate_frame(pd.read_csv(path), label_column)
    labels = [int(value) for value in frame[label_column].tolist()]
    _validate_class_balance(labels)
    feature_rows = frame.drop(columns=[label_column]).to_numpy().tolist()
    features = [[float(value) for value in row] for row in feature_rows]
    return Dataset(features=features, labels=labels)


def hash_dataset(dataset: Dataset) -> str:
    payload = json.dumps(
        {"features": dataset.features, "labels": dataset.labels},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
