"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "MoodTune AI"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/moodtune"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ML Model
    model_path: str = "app/ml/savedmodel"
    model_version: str = "bert-emotion-v1.0"
    inference_batch_size: int = 8

    # Spotify
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "https://moodtune.vercel.app"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
