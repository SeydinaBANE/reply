from pathlib import Path

import pandas as pd
import pytest

from pipeline.dataset import load_dataset
from pipeline.errors import InvalidDatasetError


def test_load_dataset_parses_features(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    pd.DataFrame({"a": [1, 2], "b": [3, 4], "label": [0, 1]}).to_csv(path, index=False)
    dataset = load_dataset(path, "label")
    assert dataset.labels == [0, 1]
    assert dataset.features == [[1.0, 3.0], [2.0, 4.0]]


def test_load_dataset_missing_label_raises(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    pd.DataFrame({"a": [1]}).to_csv(path, index=False)
    with pytest.raises(InvalidDatasetError):
        load_dataset(path, "label")


def test_load_dataset_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(InvalidDatasetError):
        load_dataset(tmp_path / "missing.csv", "label")
