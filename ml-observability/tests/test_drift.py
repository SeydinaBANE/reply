import numpy as np

from monitor.drift import population_stability_index


def test_psi_identical_distributions_is_zero() -> None:
    rng = np.random.default_rng(0)
    sample = rng.normal(size=1000)
    psi = population_stability_index(sample, sample)
    assert psi < 1e-9


def test_psi_detects_shift() -> None:
    rng = np.random.default_rng(0)
    reference = rng.normal(loc=0.0, size=1000)
    current = rng.normal(loc=3.0, size=1000)
    psi = population_stability_index(reference, current)
    assert psi > 0.25
