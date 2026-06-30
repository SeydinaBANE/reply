from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    vault_addr: str
    vault_token: str
    vault_secret_path: str = "secret/data/llm"
    redis_url: str
    rate_limit_per_minute: int = 60
    rate_limit_fail_open: bool = True


def load_settings() -> Settings:
    return Settings()
