from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import requests

from http_client.caching import FileCache, WikipediaCachePolicy
from http_client.clients import UrllibHttpClient
from http_client.interfaces import HttpClientProtocol
from http_client.policies import ResponseCache


class HtmlFetcher:
    """Warstwa pobierania HTML z opcjonalnym cache."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        timeout: int = 10,
        retries: int = 0,
        cache: ResponseCache | None = None,
    ) -> None:
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
                session=session,
                headers=headers,
                timeout=timeout,
                retries=retries,
                cache=cache,
            )
        self.http_client = http_client
        self.timeout = timeout

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.http_client.get_text(url, timeout=timeout or self.timeout)
