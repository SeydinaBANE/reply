from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    vault_addr: str
    vault_token: str
    vault_secret_path: str = "secret/data/llm"
    redis_url: str
    redis_socket_timeout: float = 5.0
    rate_limit_per_minute: int = 60
    rate_limit_fail_open: bool = True
    backend: Literal["echo", "vllm", "vertex"] = "echo"
    backend_url: str = "http://localhost:8001"
    backend_model: str = "default"
    backend_timeout_s: float = 30.0
    vertex_project: str = ""
    vertex_location: str = "us-central1"


def load_settings() -> Settings:
    return Settings()
