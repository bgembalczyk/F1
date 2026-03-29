"""Komponent obsługujący cache odpowiedzi HTTP."""

from collections.abc import Callable

from infrastructure.http_client.policies.response_cache import ResponseCache


class ResponseCacheService:
    """Fasada dla logiki odczytu/zapisu cache odpowiedzi."""

    def __init__(self, cache: ResponseCache | None) -> None:
        self._cache = cache

    def get_text(self, url: str, fetch_text: Callable[[], str]) -> str:
        if self._cache is not None:
            cached = self._cache.get(url)
            if cached is not None:
                return cached

        text = fetch_text()

        if self._cache is not None:
            self._cache.set(url, text)

        return text
