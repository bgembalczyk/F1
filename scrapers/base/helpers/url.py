"""URL normalization helpers shared across scrapers."""

from __future__ import annotations

from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from models.validation.utils import is_valid_url
from scrapers.base.url_strategy import UrlStrategy


class DefaultUrlStrategy(UrlStrategy):
    """Default URL strategy used across scraper layers."""

    def canonicalize(self, base: str, href: str | None) -> str | None:
        href_normalized = (href or "").strip()
        if not href_normalized:
            return None

        url = self.resolve_relative(base, href_normalized)
        if not self.validate(url):
            return None

        return url

    def resolve_relative(self, base: str, href: str) -> str:
        parsed_href = urlsplit(href)

        if parsed_href.scheme:
            return href

        if href.startswith("//"):
            base_scheme = urlsplit(base).scheme or "https"
            return f"{base_scheme}:{href}"

        if href.startswith("/"):
            base_parts = urlsplit(base)
            scheme = base_parts.scheme or "https"
            if base_parts.netloc:
                return urlunsplit((scheme, base_parts.netloc, href, "", ""))

        return urljoin(base, href)

    def validate(self, url: str) -> bool:
        if not is_valid_url(url):
            return False

        parsed_url = urlsplit(url)
        if "//" in parsed_url.path:
            return False

        return True


def normalize_url(base: str, href: str | None) -> str | None:
    """Backward compatible wrapper around :class:`DefaultUrlStrategy`."""
    return DefaultUrlStrategy().canonicalize(base, href)
