from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    redis_url: str
    vertex_project: str
    vertex_location: str = "europe-west1"
    embedding_model: str = "text-embedding-004"
    generation_model: str = "gemini-1.5-pro"
    top_k: int = 5
    embedding_cache_ttl: int = 86_400


def load_settings() -> Settings:
    return Settings()
