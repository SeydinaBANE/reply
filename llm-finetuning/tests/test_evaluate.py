import pytest

from conftest import MappingGenerator
from finetune.dataset import Example, validate_examples
from finetune.errors import EvaluationBaselineError, InvalidDatasetError
from finetune.evaluate import (
    EvaluationReport,
    enforce_baseline,
    evaluate_model,
    exact_match_score,
    normalized_match_score,
)
from finetune.prompt import format_prompt


def test_exact_match_score_perfect() -> None:
    assert exact_match_score(["a", "b"], ["a", "b"]) == 1.0


def test_exact_match_score_partial() -> None:
    assert exact_match_score(["a", "x"], ["a", "b"]) == 0.5


def test_normalized_match_ignores_case_and_punctuation() -> None:
    assert normalized_match_score(["Hello, World!"], ["hello world"]) == 1.0


def test_validate_examples_rejects_empty() -> None:
    with pytest.raises(InvalidDatasetError):
        validate_examples([Example(instruction=" ", response="ok")])


def test_evaluate_model_perfect_score() -> None:
    examples = [Example("q1", "a1"), Example("q2", "a2")]
    mapping = {format_prompt(example.instruction): example.response for example in examples}
    report = evaluate_model(MappingGenerator(mapping), examples)
    assert report.exact_match == 1.0
    assert report.n_examples == 2


def test_evaluate_model_partial_score() -> None:
    examples = [Example("q1", "a1"), Example("q2", "a2")]
    report = evaluate_model(MappingGenerator({format_prompt("q1"): "a1"}), examples)
    assert report.exact_match == 0.5


def test_enforce_baseline_raises_below_threshold() -> None:
    with pytest.raises(EvaluationBaselineError):
        enforce_baseline(EvaluationReport(exact_match=0.5, normalized_match=0.5, n_examples=2), 0.8)
