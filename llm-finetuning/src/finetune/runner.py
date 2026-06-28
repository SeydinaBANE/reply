import logging
from pathlib import Path

from finetune.dataset import Example
from finetune.evaluate import EvaluationReport, TextGenerator, enforce_baseline, evaluate_model
from finetune.report import write_report

logger = logging.getLogger(__name__)


def run_evaluation(
    generator: TextGenerator,
    examples: list[Example],
    baseline: float,
    report_path: Path,
) -> EvaluationReport:
    report = evaluate_model(generator, examples)
    write_report(report, report_path)
    logger.info(
        "evaluation exact_match=%.4f normalized_match=%.4f",
        report.exact_match,
        report.normalized_match,
    )
    enforce_baseline(report, baseline)
    return report
