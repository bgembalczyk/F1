from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import requests

from infrastructure.http_client.interfaces import HttpClientProtocol
from infrastructure.http_client.policies import ResponseCache
from scrapers.base.export.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.parsers import SoupParser


@dataclass(slots=True)
class ScraperOptions:
    include_urls: bool = True
    exporter: Optional[DataExporter] = None
    fetcher: HtmlFetcher | None = None
    parser: SoupParser | None = None
    session: Optional[requests.Session] = None
    headers: Optional[Dict[str, str]] = None
    http_client: Optional[HttpClientProtocol] = None
    timeout: int = 10
    retries: int = 0
    cache: ResponseCache | None = None

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("retries must be >= 0")

    @classmethod
    def from_legacy(
        cls,
        *,
        include_urls: bool | None = None,
        exporter: Optional[DataExporter] = None,
        fetcher: HtmlFetcher | None = None,
        parser: SoupParser | None = None,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        timeout: int | None = None,
        retries: int | None = None,
        cache: ResponseCache | None = None,
    ) -> "ScraperOptions | None":
        legacy_values = (
            include_urls,
            exporter,
            fetcher,
            parser,
            session,
            headers,
            http_client,
            timeout,
            retries,
            cache,
        )

        if all(value is None for value in legacy_values):
            return None

        kwargs: dict[str, object] = {}
        if include_urls is not None:
            kwargs["include_urls"] = include_urls
        if exporter is not None:
            kwargs["exporter"] = exporter
        if fetcher is not None:
            kwargs["fetcher"] = fetcher
        if parser is not None:
            kwargs["parser"] = parser
        if session is not None:
            kwargs["session"] = session
        if headers is not None:
            kwargs["headers"] = headers
        if http_client is not None:
            kwargs["http_client"] = http_client
        if timeout is not None:
            kwargs["timeout"] = timeout
        if retries is not None:
            kwargs["retries"] = retries
        if cache is not None:
            kwargs["cache"] = cache

        return cls(**kwargs)
