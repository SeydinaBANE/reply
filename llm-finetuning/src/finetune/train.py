import logging
from dataclasses import dataclass

from finetune.config import LoraConfig
from finetune.dataset import Example, validate_examples

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrainingPlan:
    base_model: str
    n_examples: int
    config: LoraConfig


def build_training_plan(
    base_model: str,
    examples: list[Example],
    config: LoraConfig,
) -> TrainingPlan:
    validated = validate_examples(examples)
    logger.info("prepared %d examples for %s", len(validated), base_model)
    return TrainingPlan(base_model=base_model, n_examples=len(validated), config=config)
