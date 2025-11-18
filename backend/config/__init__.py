from .gemini_config import MODEL as GEMINI_MODEL, gemini_client
from .openai_config import MODEL as OPENAI_MODEL, openai_client

MODEL = OPENAI_MODEL

__all__ = ['MODEL', 'GEMINI_MODEL', 'OPENAI_MODEL', 'gemini_client', 'openai_client']
