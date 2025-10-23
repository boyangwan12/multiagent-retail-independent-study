from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from app.core.config import settings

logger = logging.getLogger("fashion_forecast")

class OpenAIClient:
    """Singleton OpenAI client with retry logic"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            logger.info("Initializing OpenAI client...")
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=10.0,  # 10 second timeout
            )
            logger.info("✓ OpenAI client initialized")

    @property
    def client(self) -> OpenAI:
        """Get the OpenAI client instance"""
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        """
        Make a chat completion request with retry logic.

        Args:
            messages: List of message dicts (role, content)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Response content string

        Raises:
            openai.APIError: If API call fails after retries
        """
        try:
            logger.debug(f"Calling OpenAI with {len(messages)} messages")

            response = self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                **kwargs
            )

            content = response.choices[0].message.content
            logger.debug(f"✓ Received response ({len(content)} chars)")

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

# Singleton instance
openai_client = OpenAIClient()
