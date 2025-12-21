from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import requests

from http_client.interfaces import HttpClientProtocol
from http_client.policies import ResponseCache
from scrapers.base.exporters import DataExporter
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
