from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class ScraperConfigProtocol(Protocol):
    url: str


@runtime_checkable
class ScraperMetadataProtocol(Protocol):
    CONFIG: ScraperConfigProtocol


def resolve_scraper_url(scraper_cls: type[Any]) -> str:
    """
    Resolve scraper source URL from canonical metadata contract with legacy fallback.

    Preferred style: `scraper_cls.CONFIG.url`.
    Legacy fallback: `scraper_cls.url`.
    """
    config = getattr(scraper_cls, "CONFIG", None)
    if isinstance(config, ScraperConfigProtocol) and config.url.strip():
        return config.url

    legacy_url = getattr(scraper_cls, "url", None)
    if isinstance(legacy_url, str) and legacy_url.strip():
        return legacy_url

    msg = (
        f"{scraper_cls.__name__} does not expose scraper URL. "
        "Expected CONFIG.url (preferred) or legacy .url."
    )
    raise AttributeError(msg)
