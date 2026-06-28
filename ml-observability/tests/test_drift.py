import numpy as np

from monitor.drift import classify_drift, population_stability_index
from monitor.models import AlertLevel


def test_psi_identical_distributions_is_zero() -> None:
    rng = np.random.default_rng(0)
    sample = rng.normal(size=1000)
    assert population_stability_index(sample, sample) < 1e-9


def test_psi_detects_shift() -> None:
    rng = np.random.default_rng(0)
    reference = rng.normal(loc=0.0, size=1000)
    current = rng.normal(loc=3.0, size=1000)
    assert population_stability_index(reference, current) > 0.25


def test_classify_drift_levels() -> None:
    assert classify_drift(0.1, 0.2, 0.25) is AlertLevel.OK
    assert classify_drift(0.22, 0.2, 0.25) is AlertLevel.WARNING
    assert classify_drift(0.3, 0.2, 0.25) is AlertLevel.CRITICAL
