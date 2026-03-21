"""
Settings and configuration for LaunchLens.
Loads environment variables via Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Environment configuration from .env file."""

    # LLM Providers
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HF_API_TOKEN: str = ""
    OPENROUTER_API_KEY: str = ""

    # Data Ingestion
    SERPER_API_KEY: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Reddit (optional, for authenticated scraping)
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""

    # App
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    # LLM Model Selection
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create singleton settings instance
settings = get_settings()
