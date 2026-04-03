import warnings
from typing import Any

from infrastructure.gemini.cache import GeminiCache


class GeminiCacheService:
    """DEPRECATED: cienki shim kompatybilności wokół ``GeminiCache``."""

    def __init__(self, cache: GeminiCache | None = None) -> None:
        self._cache = cache if cache is not None else GeminiCache()
        warnings.warn(
            (
                "GeminiCacheService jest przestarzały i zostanie usunięty. "
                "Użyj bezpośrednio GeminiCache."
            ),
            DeprecationWarning,
            stacklevel=2,
        )

    @property
    def cache(self) -> GeminiCache:
        return self._cache

    def get(self, prompt: str, model: str) -> dict[str, Any] | None:
        return self._cache.get(prompt, model)

    def set(self, prompt: str, model: str, response: dict[str, Any]) -> None:
        self._cache.set(prompt, model, response)
