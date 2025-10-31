from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List
import os

class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=True, description="Debug mode")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:5174"],
        description="Allowed CORS origins (JSON array format in .env)"
    )

    # OpenAI (Required)
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name (e.g., gpt-4o-mini, gpt-4o, gpt-3.5-turbo)"
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./fashion_forecast.db",
        description="Database connection URL"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="logs/app.log", description="Log file path")

    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = Field(default=300, description="Agent timeout (5 minutes)")
    MAX_AGENT_RETRIES: int = Field(default=3, description="Max retries for agent calls")

    # Workflow Configuration
    VARIANCE_THRESHOLD_PCT: float = Field(
        default=0.20,
        description="Variance threshold for auto re-forecast (20%)"
    )

    @field_validator("VARIANCE_THRESHOLD_PCT")
    @classmethod
    def validate_variance_threshold(cls, v: float) -> float:
        """Ensure variance threshold is between 0 and 1"""
        if not 0 < v <= 1:
            raise ValueError("Variance threshold must be between 0 and 1")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )

# Singleton instance
settings = Settings()
