"""
Application Settings

Centralized configuration for the retail forecasting backend.
Loads from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Workflow Configuration
    max_reforecasts: int = int(os.getenv("MAX_REFORECASTS", "2"))
    variance_threshold: float = float(os.getenv("VARIANCE_THRESHOLD", "0.20"))

    # Pricing Configuration
    default_elasticity: float = float(os.getenv("DEFAULT_ELASTICITY", "2.0"))
    max_markdown_pct: float = float(os.getenv("MAX_MARKDOWN_PCT", "0.40"))
    markdown_rounding: float = float(os.getenv("MARKDOWN_ROUNDING", "0.05"))

    # Inventory Configuration
    default_dc_holdback_pct: float = float(os.getenv("DEFAULT_DC_HOLDBACK_PCT", "0.45"))
    default_safety_stock_pct: float = float(os.getenv("DEFAULT_SAFETY_STOCK_PCT", "0.20"))

    # Session Configuration
    session_dir: str = os.getenv("SESSION_DIR", "sessions")

    def validate(self) -> None:
        """Validate required settings are present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")


# Create global settings instance
settings = Settings()

# Convenience exports for backward compatibility
OPENAI_API_KEY = settings.openai_api_key
OPENAI_MODEL = settings.openai_model
