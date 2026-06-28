from pathlib import Path

import yaml
from pydantic import BaseModel


class LoraConfig(BaseModel):
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    learning_rate: float = 2e-4
    epochs: int = 3
    batch_size: int = 8
    target_modules: list[str] = ["q_proj", "v_proj"]


def load_lora_config(path: Path) -> LoraConfig:
    raw: dict[str, object] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return LoraConfig.model_validate(raw)
