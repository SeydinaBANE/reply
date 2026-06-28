from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql://obs:obs@localhost:5432/obs"
    redis_url: str = "redis://localhost:6379/0"
    psi_warning_threshold: float = 0.2
    psi_critical_threshold: float = 0.25


def load_settings() -> Settings:
    return Settings()
