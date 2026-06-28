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
            _dataset(), NoOpTracker(), _FakeRegistry(), "churn", tmp_path / "m.joblib", threshold=1.01
        )
