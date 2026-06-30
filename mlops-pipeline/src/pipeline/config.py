from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mlflow_tracking_uri: str
    jfrog_url: str
    jfrog_repo: str
    jfrog_token: str
    vertex_project: str
    vertex_location: str = "europe-west1"
    model_name: str = "model"
    eval_threshold: float = 0.8
    train_seed: int = 42


def load_settings() -> Settings:
    return Settings()
