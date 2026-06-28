import pytest

from finetune.dataset import Example, validate_examples
from finetune.errors import InvalidDatasetError
from finetune.evaluate import exact_match_score


def test_exact_match_score_perfect() -> None:
    assert exact_match_score(["a", "b"], ["a", "b"]) == 1.0


def test_exact_match_score_partial() -> None:
    assert exact_match_score(["a", "x"], ["a", "b"]) == 0.5


def test_validate_examples_rejects_empty() -> None:
    with pytest.raises(InvalidDatasetError):
        validate_examples([Example(instruction=" ", response="ok")])
