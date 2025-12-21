from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING


import requests

from infrastructure.http_client.interfaces import HttpClientProtocol
from infrastructure.http_client.policies import ResponseCache

if TYPE_CHECKING:
    from scrapers.base.export.exporters import DataExporter
    from scrapers.base.html_fetcher import HtmlFetcher
    from scrapers.base.parsers import SoupParser


@dataclass(frozen=True)
class HttpConfig:
    session: requests.Session | None = None
    headers: dict[str, str] | None = None
    user_agent: str | None = None
    timeout: int = 10
    retries: int = 0
    cache: ResponseCache | None = None
    http_client: HttpClientProtocol | None = None

    def merged_headers(self) -> dict[str, str] | None:
        merged: dict[str, str] = {}
        if self.user_agent:
            merged["User-Agent"] = self.user_agent
        if self.headers:
            merged.update(self.headers)
        return merged or None


def default_http_config() -> HttpConfig:
    return HttpConfig()


@dataclass(frozen=True)
class ScraperConfig:
    include_urls: bool = True
    exporter: DataExporter | None = None
    fetcher: HtmlFetcher | None = None
    parser: SoupParser | None = None
    http: HttpConfig = field(default_factory=default_http_config)


def default_scraper_config() -> ScraperConfig:
    return ScraperConfig()


def default_config() -> ScraperConfig:
    return default_scraper_config()
