import numpy as np
import pytest

from monitor.models import AlertLevel
from monitor.monitoring import evaluate_drift


def test_evaluate_drift_no_shift_is_ok() -> None:
    rng = np.random.default_rng(0)
    reference = rng.normal(size=(500, 2)).tolist()
    current = rng.normal(size=(500, 2)).tolist()
    result = evaluate_drift(reference, current, warning_threshold=0.2, critical_threshold=0.25)
    assert result.level is AlertLevel.OK


def test_evaluate_drift_detects_critical_shift() -> None:
    rng = np.random.default_rng(0)
    reference = rng.normal(loc=0.0, size=(500, 2)).tolist()
    current = (rng.normal(loc=0.0, size=(500, 2)) + 4.0).tolist()
    result = evaluate_drift(reference, current, warning_threshold=0.2, critical_threshold=0.25)
    assert result.level is AlertLevel.CRITICAL
    assert result.psi > 0.25


def test_evaluate_drift_dimension_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        evaluate_drift([[1.0, 2.0]], [[1.0]], warning_threshold=0.2, critical_threshold=0.25)
