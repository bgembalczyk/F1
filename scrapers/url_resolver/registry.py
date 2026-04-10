from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from models.validation.helpers import is_valid_url
from scrapers.section.aliases import builtin_aliases_for_target

_WIKIPEDIA_DOMAINS = {
    "wikipedia",
    "seasons",
    "drivers",
    "constructors",
    "circuits",
    "grands_prix",
}


@dataclass(frozen=True)
class UrlResolverStrategyRegistry:
    """Central registry resolving URL/section behavior by domain strategy."""

    default_domain: str = "generic"

    def resolve_url(
        self,
        *,
        base_url: str,
        href: str | None,
        domain: str | None = None,
    ) -> str | None:
        href_normalized = (href or "").strip()
        if not href_normalized:
            return None

        resolved_domain = self._resolve_domain(base_url=base_url, domain=domain)
        if resolved_domain == "wikipedia":
            resolved = self._resolve_wikipedia_url(
                base_url=base_url,
                href=href_normalized,
            )
        else:
            resolved = self._resolve_generic_url(
                base_url=base_url,
                href=href_normalized,
            )

        if not resolved or not is_valid_url(resolved):
            return None

        parsed_url = urlsplit(resolved)
        if "//" in parsed_url.path:
            return None
        return resolved

    def section_aliases_for(self, *, domain: str, section_id: str) -> set[str]:
        if self._resolve_domain(base_url="", domain=domain) != "wikipedia":
            return set()
        return builtin_aliases_for_target(section_id, domain=domain)

    def fallback_canonical_url(
        self,
        *,
        domain: str,
        base_url: str,
        **context: str,
    ) -> str | None:
        resolved_domain = self._resolve_domain(base_url=base_url, domain=domain)
        if resolved_domain != "wikipedia" or domain != "seasons":
            return None

        year = context.get("year")
        season_page_title = context.get("season_page_title")
        if not year or not season_page_title:
            return None

        return self.resolve_url(
            base_url=base_url,
            href=f"/wiki/{season_page_title}",
            domain=resolved_domain,
        )

    @staticmethod
    def _resolve_wikipedia_url(*, base_url: str, href: str) -> str:
        parsed_href = urlsplit(href)
        if parsed_href.scheme:
            return href

        if href.startswith("//"):
            base_scheme = urlsplit(base_url).scheme or "https"
            return f"{base_scheme}:{href}"

        if href.startswith("/"):
            base_parts = urlsplit(base_url)
            scheme = base_parts.scheme or "https"
            if base_parts.netloc:
                return urlunsplit((scheme, base_parts.netloc, href, "", ""))

        return urljoin(base_url, href)

    @staticmethod
    def _resolve_generic_url(*, base_url: str, href: str) -> str:
        parsed_href = urlsplit(href)
        if parsed_href.scheme:
            return href
        return urljoin(base_url, href)

    @staticmethod
    def _resolve_domain(*, base_url: str, domain: str | None) -> str:
        normalized_domain = (domain or "").strip().lower()
        if normalized_domain in _WIKIPEDIA_DOMAINS:
            return "wikipedia"

        hostname = urlsplit(base_url).hostname or ""
        if hostname == "wikipedia.org" or hostname.endswith(".wikipedia.org"):
            return "wikipedia"

        return "generic"


DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY = UrlResolverStrategyRegistry()


__all__ = [
    "DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY",
    "UrlResolverStrategyRegistry",
]
