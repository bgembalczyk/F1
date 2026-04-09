from dataclasses import dataclass

from infrastructure.http.policies.http import HttpPolicy
from infrastructure.http.protocols import HttpClientProtocol
from infrastructure.http.protocols.text_cache import TextCacheProtocol
from scrapers.html_fetcher import HtmlFetcher
from scrapers.source_adapter import SourceAdapter


@dataclass(frozen=True, slots=True)
class ScraperRuntime:
    policy: HttpPolicy
    http_client: HttpClientProtocol
    cache_adapter: TextCacheProtocol | None
    fetcher: HtmlFetcher
    source_adapter: SourceAdapter
