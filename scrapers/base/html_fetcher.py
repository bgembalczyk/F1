from __future__ import annotations

from pathlib import Path

from infrastructure.http_client.caching import FileCache, WikipediaCachePolicy
from infrastructure.http_client.clients import UrllibHttpClient

from scrapers.config import HttpConfig, default_http_config


class HtmlFetcher:
    """Warstwa pobierania HTML z opcjonalnym cache."""

    def __init__(self, *, config: HttpConfig | None = None) -> None:
        config = config or default_http_config()

        http_client = config.http_client
        cache = config.cache
        headers = config.merged_headers()

        if http_client is None:
            if cache is None:
                cache_dir = Path(__file__).resolve().parents[2] / "data" / "wiki_cache"
                cache = WikipediaCachePolicy(
                    FileCache(
                        cache_dir=cache_dir,
                        ttl_seconds=30 * 24 * 60 * 60,
                    )
                )

            http_client = UrllibHttpClient(
                session=config.session,
                config=None,  # używamy "legacy overrides" (kompatybilne z clients.py)
                headers=headers,
                timeout=config.timeout,
                retries=config.retries,
                cache=cache,
            )

        self.http_client = http_client
        self.timeout = config.timeout

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.http_client.get_text(url, timeout=timeout or self.timeout)
