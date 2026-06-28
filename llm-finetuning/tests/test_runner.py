import json
from pathlib import Path

import pytest

from conftest import MappingGenerator
from finetune.dataset import Example
from finetune.errors import EvaluationBaselineError
from finetune.prompt import format_prompt
from finetune.report import to_markdown
from finetune.evaluate import EvaluationReport
from finetune.runner import run_evaluation


def test_run_evaluation_writes_report_and_passes(tmp_path: Path) -> None:
    examples = [Example("q1", "a1")]
    generator = MappingGenerator({format_prompt("q1"): "a1"})
    report_path = tmp_path / "report.json"
    report = run_evaluation(generator, examples, baseline=0.5, report_path=report_path)

    assert report.exact_match == 1.0
    written = json.loads(report_path.read_text(encoding="utf-8"))
    assert written["n_examples"] == 1


def test_run_evaluation_baseline_failure_raises(tmp_path: Path) -> None:
    examples = [Example("q1", "a1")]
    generator = MappingGenerator({})
    with pytest.raises(EvaluationBaselineError):
        run_evaluation(generator, examples, baseline=0.9, report_path=tmp_path / "report.json")


def test_to_markdown_contains_metrics() -> None:
    markdown = to_markdown(EvaluationReport(exact_match=0.5, normalized_match=0.75, n_examples=4))
    assert "exact_match: 0.5000" in markdown
    assert "normalized_match: 0.7500" in markdown
