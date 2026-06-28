import json
from dataclasses import dataclass
from pathlib import Path

from finetune.errors import InvalidDatasetError


@dataclass(frozen=True)
class Example:
    instruction: str
    response: str


def validate_examples(examples: list[Example]) -> list[Example]:
    if not examples:
        raise InvalidDatasetError("dataset is empty")
    for index, example in enumerate(examples):
        if not example.instruction.strip() or not example.response.strip():
            raise InvalidDatasetError(f"example {index} has empty field")
    return examples


def load_jsonl(path: Path) -> list[Example]:
    if not path.is_file():
        raise InvalidDatasetError(f"dataset not found: {path}")

    examples: list[Example] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
            examples.append(
                Example(instruction=str(payload["instruction"]), response=str(payload["response"]))
            )
        except (json.JSONDecodeError, KeyError) as exc:
            raise InvalidDatasetError(f"invalid record at line {number + 1}: {exc}") from exc
    return validate_examples(examples)
