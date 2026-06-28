from dataclasses import dataclass

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
