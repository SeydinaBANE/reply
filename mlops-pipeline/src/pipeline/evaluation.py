import logging

from pipeline.errors import EvaluationGateError
from pipeline.models import EvaluationReport

logger = logging.getLogger(__name__)


def passes_gate(
    report: EvaluationReport,
    threshold: float,
    baseline: float | None = None,
    tolerance: float = 0.0,
) -> bool:
    if report.accuracy < threshold:
        return False
    if baseline is not None and report.accuracy < baseline - tolerance:
        return False
    return True


def enforce_gate(
    report: EvaluationReport,
    threshold: float,
    baseline: float | None = None,
    tolerance: float = 0.0,
) -> None:
    if report.accuracy < threshold:
        raise EvaluationGateError(
            f"accuracy {report.accuracy:.4f} below threshold {threshold:.4f}"
        )
    if baseline is not None and report.accuracy < baseline - tolerance:
        raise EvaluationGateError(
            f"accuracy {report.accuracy:.4f} regressed vs baseline {baseline:.4f}"
            f" (tolerance {tolerance:.4f})"
        )
    logger.info("evaluation gate passed (accuracy=%.4f)", report.accuracy)
