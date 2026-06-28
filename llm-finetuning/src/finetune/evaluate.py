import re
from dataclasses import dataclass
from typing import Protocol

from finetune.dataset import Example
from finetune.errors import EvaluationBaselineError
from finetune.prompt import format_prompt

_NORMALIZE_PATTERN = re.compile(r"[^a-z0-9 ]")


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class EvaluationReport:
    exact_match: float
    normalized_match: float
    n_examples: int


def exact_match_score(predictions: list[str], references: list[str]) -> float:
    _check_lengths(predictions, references)
    if not predictions:
        return 0.0
    matches = sum(1 for pred, ref in zip(predictions, references) if pred.strip() == ref.strip())
    return matches / len(predictions)


def normalized_match_score(predictions: list[str], references: list[str]) -> float:
    _check_lengths(predictions, references)
    if not predictions:
        return 0.0
    matches = sum(
        1 for pred, ref in zip(predictions, references) if _normalize(pred) == _normalize(ref)
    )
    return matches / len(predictions)


def evaluate_model(generator: TextGenerator, examples: list[Example]) -> EvaluationReport:
    predictions = [generator.generate(format_prompt(example.instruction)) for example in examples]
    references = [example.response for example in examples]
    return EvaluationReport(
        exact_match=exact_match_score(predictions, references),
        normalized_match=normalized_match_score(predictions, references),
        n_examples=len(examples),
    )


def enforce_baseline(report: EvaluationReport, baseline: float) -> None:
    if report.exact_match < baseline:
        raise EvaluationBaselineError(
            f"exact_match {report.exact_match:.4f} below baseline {baseline:.4f}"
        )


def _check_lengths(predictions: list[str], references: list[str]) -> None:
    if len(predictions) != len(references):
        raise ValueError("predictions and references length mismatch")


def _normalize(text: str) -> str:
    return _NORMALIZE_PATTERN.sub("", text.lower()).strip()
