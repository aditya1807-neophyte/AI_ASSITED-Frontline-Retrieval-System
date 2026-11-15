from functools import lru_cache
from typing import Optional
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Frontline Knowledge Workspace API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./data/frontline.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    jwt_secret_key: str = "fieldguide-dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    embedding_index_dir: str = "./data/embeddings"

    # LLM & Gemini configuration
    llm_provider: str = "gemini"
    gemini_api_key: str = "your_gemini_api_key_here"
    gemini_model: str = "gemini-3.5-flash"
    vite_gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_api_url: Optional[str] = None
    llm_model: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=(".env", "../frontend/.env", "../.env"),
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
