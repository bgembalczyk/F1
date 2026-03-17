"""Contract and shared implementation helpers for URL resolution strategies."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class UrlStrategy(ABC):
    """Contract for URL resolution/validation logic used by scrapers."""

    @abstractmethod
    def canonicalize(self, base: str, href: str | None) -> str | None:
        """Return normalized absolute URL or ``None`` when input cannot be used."""

    @abstractmethod
    def resolve_relative(self, base: str, href: str) -> str:
        """Resolve a possibly relative ``href`` into an absolute URL candidate."""

    @abstractmethod
    def validate(self, url: str) -> bool:
        """Validate that URL can be safely used by the scraping pipeline."""

