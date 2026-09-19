  # backend/core/ai/factory.py

from django.conf import settings
from .base import LLMProvider
from .gemini import GeminiProvider
from .groq import GroqProvider


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    """
    Factory function to get the correct LLM provider.
    Default provider is taken from settings.DEFAULT_LLM_PROVIDER
    """
    name = (provider_name or getattr(settings, "DEFAULT_LLM_PROVIDER", "gemini")).lower()

    if name == "gemini":
        return GeminiProvider()
    elif name == "groq":
        return GroqProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {name}")