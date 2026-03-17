from __future__ import annotations

from dataclasses import dataclass

from scrapers.base.helpers.url import DefaultUrlStrategy

WIKIPEDIA_SOURCE_SLUG = "wikipedia"
WIKIPEDIA_BASE_HOST = "en.wikipedia.org"


@dataclass(frozen=True)
class SeedUrlResolver:
    """Resolve source slugs to canonical absolute seed URLs."""

    url_strategy: DefaultUrlStrategy = DefaultUrlStrategy()

    def resolve_source_url(self, source_slug: str, article_path: str) -> str:
        source = source_slug.strip().lower()
        if not source:
            raise ValueError("source_slug cannot be empty")

        path = article_path.strip()
        if not path:
            raise ValueError("article_path cannot be empty")

        host = WIKIPEDIA_BASE_HOST if source == WIKIPEDIA_SOURCE_SLUG else source
        candidate_base = f"https://{host}"
        candidate_url = self.url_strategy.resolve_relative(candidate_base, path)
        canonical_url = self.url_strategy.canonicalize(candidate_base, candidate_url)
        if not canonical_url:
            msg = f"Could not resolve URL for source_slug='{source_slug}' and path='{article_path}'"
            raise ValueError(msg)

        return canonical_url
