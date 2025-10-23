"""Agent configuration using standard OpenAI API."""

from dataclasses import dataclass
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger("fashion_forecast")


@dataclass
class AgentConfig:
    """Configuration for OpenAI agents (adapted for standard OpenAI API)."""

    # OpenAI client
    openai_client: OpenAI

    # Model configuration
    model: str
    temperature: float = 0.2  # Low temperature for deterministic business logic
    max_tokens: int = 4000

    # Agent behavior
    timeout_seconds: int = 300  # 5 minutes default
    max_retries: int = 3

    @classmethod
    def from_settings(cls) -> "AgentConfig":
        """
        Create AgentConfig from application settings.

        Uses standard OpenAI API (not Azure) as configured in settings.

        Returns:
            AgentConfig instance
        """
        logger.info("Creating AgentConfig from settings (standard OpenAI)")

        # Initialize OpenAI client
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=float(settings.AGENT_TIMEOUT_SECONDS)
        )

        return cls(
            openai_client=client,
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            max_tokens=4000,
            timeout_seconds=settings.AGENT_TIMEOUT_SECONDS,
            max_retries=settings.MAX_AGENT_RETRIES
        )


# Singleton instance
_agent_config: AgentConfig | None = None


def get_agent_config() -> AgentConfig:
    """
    Get or create the singleton AgentConfig instance.

    Returns:
        AgentConfig singleton
    """
    global _agent_config
    if _agent_config is None:
        _agent_config = AgentConfig.from_settings()
        logger.info(" AgentConfig singleton initialized")
    return _agent_config
