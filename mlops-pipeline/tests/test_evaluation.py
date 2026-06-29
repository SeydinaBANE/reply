import pytest

from pipeline.errors import EvaluationGateError
from pipeline.evaluation import enforce_gate, passes_gate
from pipeline.models import EvaluationReport


def _report(accuracy: float) -> EvaluationReport:
    return EvaluationReport(accuracy=accuracy, f1=accuracy, n_train=10, n_test=2)


def test_passes_gate_above_threshold() -> None:
    assert passes_gate(_report(0.9), 0.8)


def test_passes_gate_below_threshold() -> None:
    assert not passes_gate(_report(0.5), 0.8)


def test_enforce_gate_raises_below_threshold() -> None:
    with pytest.raises(EvaluationGateError):
        enforce_gate(_report(0.5), 0.8)


def test_passes_gate_below_baseline() -> None:
    assert not passes_gate(_report(0.85), 0.8, baseline=0.9)


def test_passes_gate_within_baseline_tolerance() -> None:
    assert passes_gate(_report(0.88), 0.8, baseline=0.9, tolerance=0.05)


def test_enforce_gate_raises_on_baseline_regression() -> None:
    with pytest.raises(EvaluationGateError):
        enforce_gate(_report(0.85), 0.8, baseline=0.95)
