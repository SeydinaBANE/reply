import numpy as np

from monitor.drift import classify_drift, population_stability_index
from monitor.errors import DriftComputationError
from monitor.models import DriftResult


def evaluate_drift(
    reference: list[list[float]],
    current: list[list[float]],
    warning_threshold: float,
    critical_threshold: float,
) -> DriftResult:
    ref = np.asarray(reference, dtype=np.float64)
    cur = np.asarray(current, dtype=np.float64)
    if ref.ndim != 2 or cur.ndim != 2 or ref.shape[1] != cur.shape[1]:
        raise DriftComputationError("reference and current must be 2D with matching feature dimension")

    per_feature = [
        population_stability_index(ref[:, column], cur[:, column])
        for column in range(ref.shape[1])
    ]
    worst = max(per_feature) if per_feature else 0.0
    return DriftResult(
        psi=float(worst),
        level=classify_drift(worst, warning_threshold, critical_threshold),
    )
