from contextlib import AbstractContextManager, nullcontext
from pathlib import Path

import pytest

from pipeline.errors import EvaluationGateError
from pipeline.models import Dataset
from pipeline.runner import run_pipeline
from pipeline.tracker import NoOpTracker


class _FakeRegistry:
    def __init__(self) -> None:
        self.pushed: list[str] = []

    def push(self, local_path: Path, remote_name: str) -> str:
        self.pushed.append(remote_name)
        return f"https://registry/{remote_name}"


class _RecordingTracker:
    def __init__(self) -> None:
        self.params: dict[str, object] = {}
        self.metrics: dict[str, float] = {}
        self.models: list[str] = []
        self.artifacts: list[Path] = []

    def run(self, tags: dict[str, str]) -> AbstractContextManager[None]:
        return nullcontext()

    def log_params(self, params: dict[str, object]) -> None:
        self.params.update(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self.metrics.update(metrics)

    def log_artifact(self, path: Path) -> None:
        self.artifacts.append(path)

    def log_model(self, model: object, name: str, sample: list[list[float]]) -> None:
        self.models.append(name)


def _dataset() -> Dataset:
    positive = [[float(i), float(i)] for i in range(20)]
    negative = [[float(-i), float(-i)] for i in range(1, 21)]
    return Dataset(features=positive + negative, labels=[1] * 20 + [0] * 20)


def test_run_pipeline_passes_gate_and_pushes(tmp_path: Path) -> None:
    registry = _FakeRegistry()
    report = run_pipeline(
        _dataset(), NoOpTracker(), registry, "churn", tmp_path / "m.joblib", threshold=0.0
    )
    assert report.accuracy >= 0.0
    assert registry.pushed == ["churn.joblib"]


def test_run_pipeline_gate_failure_raises(tmp_path: Path) -> None:
    with pytest.raises(EvaluationGateError):
        run_pipeline(
            _dataset(),
            NoOpTracker(),
            _FakeRegistry(),
            "churn",
            tmp_path / "m.joblib",
            threshold=1.01,
        )


def test_run_pipeline_gate_failure_does_not_publish(tmp_path: Path) -> None:
    registry = _FakeRegistry()
    tracker = _RecordingTracker()
    model_path = tmp_path / "m.joblib"
    with pytest.raises(EvaluationGateError):
        run_pipeline(_dataset(), tracker, registry, "churn", model_path, threshold=1.01)
    assert registry.pushed == []
    assert not model_path.exists()
    assert tracker.models == []
    assert "accuracy" in tracker.metrics


def test_run_pipeline_logs_params_and_model(tmp_path: Path) -> None:
    tracker = _RecordingTracker()
    run_pipeline(_dataset(), tracker, _FakeRegistry(), "churn", tmp_path / "m.joblib", threshold=0.0)
    assert tracker.params["model_name"] == "churn"
    assert tracker.params["seed"] == 42
    assert "dataset_hash" in tracker.params
    assert tracker.models == ["churn"]


def test_run_pipeline_baseline_regression_does_not_publish(tmp_path: Path) -> None:
    registry = _FakeRegistry()
    with pytest.raises(EvaluationGateError):
        run_pipeline(
            _dataset(),
            NoOpTracker(),
            registry,
            "churn",
            tmp_path / "m.joblib",
            threshold=0.0,
            baseline=1.1,
        )
    assert registry.pushed == []
