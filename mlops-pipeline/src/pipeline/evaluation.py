import logging

from pipeline.errors import EvaluationGateError
from pipeline.models import EvaluationReport

logger = logging.getLogger(__name__)


def passes_gate(report: EvaluationReport, threshold: float) -> bool:
    return report.accuracy >= threshold


def enforce_gate(report: EvaluationReport, threshold: float) -> None:
    if not passes_gate(report, threshold):
        raise EvaluationGateError(
            f"accuracy {report.accuracy:.4f} below threshold {threshold:.4f}"
        )
    logger.info("evaluation gate passed (accuracy=%.4f)", report.accuracy)
