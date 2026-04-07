import warnings

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

    def __getattr__(self, name: str) -> object:
        return getattr(self.cache, name)
