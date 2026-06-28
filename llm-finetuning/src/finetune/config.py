from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    vertex_project: str
    vertex_location: str = "europe-west1"
    base_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    eval_baseline: float = 0.7


def load_settings() -> Settings:
    return Settings()
