import warnings
from typing import Any

from infrastructure.gemini.cache import GeminiCache


class GeminiCacheService:
    """Backward-compatible wrapper around :class:`GeminiCache`."""

    def __init__(self, cache: GeminiCache) -> None:
        warnings.warn(
            "GeminiCacheService jest przestarzały — użyj GeminiCache.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.cache = cache

    def get(self, question: str, model: str) -> dict[str, Any] | None:
        return self.cache.get(question, model)

    def set(self, question: str, model: str, response: dict[str, Any]) -> None:
        self.cache.set(question, model, response)
