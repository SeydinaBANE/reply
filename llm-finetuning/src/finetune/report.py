import json
from pathlib import Path

from finetune.evaluate import EvaluationReport


def to_markdown(report: EvaluationReport) -> str:
    return (
        "# Evaluation Report\n\n"
        f"- examples: {report.n_examples}\n"
        f"- exact_match: {report.exact_match:.4f}\n"
        f"- normalized_match: {report.normalized_match:.4f}\n"
    )


def write_report(report: EvaluationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "exact_match": report.exact_match,
        "normalized_match": report.normalized_match,
        "n_examples": report.n_examples,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
