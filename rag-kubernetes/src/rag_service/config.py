from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    redis_url: str
    vertex_project: str
    api_key: str
    vertex_location: str = "europe-west1"
    embedding_model: str = "text-embedding-004"
    embedding_dim: int = 768
    generation_model: str = "gemini-1.5-pro"
    top_k: int = 5
    embedding_cache_ttl: int = 86_400
    chunk_size: int = 800
    chunk_overlap: int = 100
    pool_min_size: int = 1
    pool_max_size: int = 10
    pg_command_timeout: float = 10.0
    redis_socket_timeout: float = 2.0
    vertex_timeout: float = 30.0
    vertex_max_attempts: int = 3
    vertex_backoff_base: float = 0.5
    log_level: str = "INFO"


def load_settings() -> Settings:
    return Settings()
