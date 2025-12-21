from __future__ import annotations

from pathlib import Path

from infrastructure.http_client.caching import FileCache, WikipediaCachePolicy
from infrastructure.http_client.clients import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig

from scrapers.base.source_adapter import SourceAdapter
from scrapers.config import HttpConfig, default_http_config


class HtmlFetcher(SourceAdapter[str]):
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

            # Używamy HttpClientConfig
            client_config = HttpClientConfig(
                headers=headers,
                timeout=config.timeout,
                retries=config.retries,
                cache=cache,
            )

            http_client = UrllibHttpClient(
                session=config.session,
                config=client_config,
            )

        self.http_client = http_client
        self.timeout = config.timeout

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.http_client.get_text(url, timeout=timeout or self.timeout)

    def get(self, source: str | None = None, **kwargs: object) -> str:
        if source is None:
            raise ValueError("HtmlFetcher wymaga URL-a jako źródła.")
        timeout = kwargs.get("timeout")
        return self.get_text(
            source, timeout=timeout if isinstance(timeout, int) else None
        )
