from pathlib import Path

from pipeline.models import Dataset
from pipeline.train import save_model, train_model


def toy_dataset() -> Dataset:
    positive = [[float(i), float(i)] for i in range(20)]
    negative = [[float(-i), float(-i)] for i in range(1, 21)]
    return Dataset(features=positive + negative, labels=[1] * 20 + [0] * 20)


def test_train_model_returns_metrics() -> None:
    _, report = train_model(toy_dataset(), seed=0)
    assert 0.0 <= report.accuracy <= 1.0
    assert report.n_train + report.n_test == 40


def test_train_model_learns_separable_data() -> None:
    _, report = train_model(toy_dataset(), seed=0)
    assert report.accuracy >= 0.8


def test_save_model_writes_file(tmp_path: Path) -> None:
    model, _ = train_model(toy_dataset(), seed=0)
    path = tmp_path / "model.joblib"
    save_model(model, path)
    assert path.is_file()
