import numpy as np
from numpy.typing import NDArray

from monitor.models import AlertLevel


def population_stability_index(
    reference: NDArray[np.float64],
    current: NDArray[np.float64],
    bins: int = 10,
) -> float:
    edges = np.histogram_bin_edges(reference, bins=bins)
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)

    ref_ratio = _to_ratio(ref_counts)
    cur_ratio = _to_ratio(cur_counts)

    contributions = (cur_ratio - ref_ratio) * np.log(cur_ratio / ref_ratio)
    return float(np.sum(contributions))


def classify_drift(psi: float, warning_threshold: float, critical_threshold: float) -> AlertLevel:
    if psi >= critical_threshold:
        return AlertLevel.CRITICAL
    if psi >= warning_threshold:
        return AlertLevel.WARNING
    return AlertLevel.OK


def _to_ratio(counts: NDArray[np.int_], epsilon: float = 1e-6) -> NDArray[np.float64]:
    ratio = counts.astype(np.float64) / max(counts.sum(), 1)
    clipped: NDArray[np.float64] = np.clip(ratio, epsilon, None)
    return clipped
