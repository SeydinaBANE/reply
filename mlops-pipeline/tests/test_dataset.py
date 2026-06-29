from pathlib import Path

import pandas as pd
import pytest

from pipeline.dataset import hash_dataset, load_dataset
from pipeline.errors import InvalidDatasetError
from pipeline.models import Dataset


def _write(path: Path, frame: pd.DataFrame) -> Path:
    frame.to_csv(path, index=False)
    return path


def test_load_dataset_parses_features(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "data.csv",
        pd.DataFrame({"a": [1, 2, 3, 4], "b": [3, 4, 5, 6], "label": [0, 0, 1, 1]}),
    )
    dataset = load_dataset(path, "label")
    assert dataset.labels == [0, 0, 1, 1]
    assert dataset.features[0] == [1.0, 3.0]


def test_load_dataset_missing_label_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "data.csv", pd.DataFrame({"a": [1]}))
    with pytest.raises(InvalidDatasetError):
        load_dataset(path, "label")


def test_load_dataset_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(InvalidDatasetError):
        load_dataset(tmp_path / "missing.csv", "label")


def test_load_dataset_non_numeric_feature_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "data.csv",
        pd.DataFrame({"a": ["x", "y", "z", "w"], "label": [0, 0, 1, 1]}),
    )
    with pytest.raises(InvalidDatasetError):
        load_dataset(path, "label")


def test_load_dataset_single_class_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "data.csv",
        pd.DataFrame({"a": [1, 2, 3], "label": [1, 1, 1]}),
    )
    with pytest.raises(InvalidDatasetError):
        load_dataset(path, "label")


def test_load_dataset_underfilled_class_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "data.csv",
        pd.DataFrame({"a": [1, 2, 3], "label": [0, 1, 1]}),
    )
    with pytest.raises(InvalidDatasetError):
        load_dataset(path, "label")


def test_hash_dataset_is_deterministic() -> None:
    first = Dataset(features=[[1.0, 2.0]], labels=[1])
    second = Dataset(features=[[1.0, 2.0]], labels=[1])
    assert hash_dataset(first) == hash_dataset(second)


def test_hash_dataset_changes_with_content() -> None:
    base = Dataset(features=[[1.0, 2.0]], labels=[1])
    other = Dataset(features=[[1.0, 2.1]], labels=[1])
    assert hash_dataset(base) != hash_dataset(other)
