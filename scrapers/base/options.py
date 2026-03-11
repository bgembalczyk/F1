from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import cast

from infrastructure.http_client.clients.urllib_http import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from infrastructure.http_client.policies.defaults import (
    DEFAULT_HTTP_BACKOFF_SECONDS,
)
from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.cache_adapter import CacheAdapter
from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.cache_adapter import FileCacheBackend
from scrapers.base.export.exporters import DataExporter
from scrapers.base.helpers.http import default_http_policy
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.parsers.soup import SoupParser
from scrapers.base.post_processors import RecordPostProcessor
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import RecordValidator


@dataclass(slots=True)
class ScraperOptions:
    """
    Konfiguracja scrapera.
    """

    include_urls: bool = True
    exporter: Optional[DataExporter] = None
    fetcher: HtmlFetcher | None = None
    source_adapter: SourceAdapter | None = None
    parser: SoupParser | None = None
    policy: HttpPolicy | None = None
    http_client: Optional[HttpClientProtocol] = None
    validator: RecordValidator | None = None
    validation_mode: str = "soft"
    debug_dir: Path | None = None
    cache_dir: Path | str | None = None
    cache_ttl: int | None = None
    cache_adapter: CacheBackend | None = None
    http_timeout: int | None = None
    http_retries: int | None = None
    http_backoff_seconds: float | None = None
    normalize_empty_values: bool = True
    record_factory: Callable[[Mapping[str, Any]], Any] | type | None = None
    run_id: str | None = None
    transformers: list[RecordTransformer] | None = None
    post_processors: list[RecordPostProcessor] | None = None
    quality_report: bool = False
    error_report: bool = False

    def __post_init__(self) -> None:
        if self.policy is None:
            self.policy = default_http_policy()
        if self.transformers is None:
            self.transformers = []
        if self.post_processors is None:
            self.post_processors = []

    def to_http_policy(self) -> HttpPolicy:
        if self.policy is None:
            self.policy = default_http_policy()
        policy = self.policy
        resolved_timeout = (
            self.http_timeout if self.http_timeout is not None else policy.timeout
        )
        resolved_retries = (
            self.http_retries if self.http_retries is not None else policy.retries
        )
        if resolved_timeout != policy.timeout or resolved_retries != policy.retries:
            policy = replace(
                policy,
                timeout=resolved_timeout,
                retries=resolved_retries,
            )
            self.policy = policy
        return policy

    def _ensure_http_client(self, policy: HttpPolicy) -> HttpClientProtocol:
        if self.http_client is None:
            backoff_seconds = (
                self.http_backoff_seconds
                if self.http_backoff_seconds is not None
                else DEFAULT_HTTP_BACKOFF_SECONDS
            )
            client_config = HttpClientConfig(
                timeout=policy.timeout,
                retries=policy.retries,
                backoff_seconds=backoff_seconds,
                cache=policy.cache,
            )
            self.http_client = cast(
                HttpClientProtocol,
                UrllibHttpClient(
                    config=client_config,
                ),
            )
        return self.http_client

    def _resolve_cache_adapter(self) -> CacheBackend | None:
        if self.cache_adapter is not None:
            return self.cache_adapter
        if self.cache_dir is not None:
            ttl_seconds = self.cache_ttl or 0
            self.cache_adapter = FileCacheBackend(
                cache_dir=self.cache_dir,
                ttl_seconds=ttl_seconds,
            )
        return self.cache_adapter

    def with_fetcher(self, *, policy: HttpPolicy | None = None) -> HtmlFetcher:
        if policy is not None:
            self.policy = policy

        from scrapers.base.html_fetcher import HtmlFetcher

        cache_adapter = self._resolve_cache_adapter()

        if self.fetcher is None:
            if isinstance(self.source_adapter, HtmlFetcher):
                self.fetcher = self.source_adapter
            else:
                resolved_policy = self.to_http_policy()
                http_client = self._ensure_http_client(resolved_policy)
                self.fetcher = HtmlFetcher(
                    policy=resolved_policy,
                    http_client=http_client,
                    cache_adapter=cache_adapter,
                )
                if self.source_adapter is None:
                    self.source_adapter = self.fetcher
        elif cache_adapter is not None:
            self.fetcher.set_cache(cache_adapter)
        return self.fetcher

    def with_source_adapter(
            self,
            *,
            policy: HttpPolicy | None = None,
    ) -> SourceAdapter:
        from scrapers.base.html_fetcher import HtmlFetcher

        if policy is not None:
            self.policy = policy

        if self.source_adapter is None:
            if self.fetcher is not None:
                self.source_adapter = self.fetcher
            else:
                resolved_policy = self.to_http_policy()
                http_client = self._ensure_http_client(resolved_policy)
                self.fetcher = HtmlFetcher(
                    policy=resolved_policy,
                    http_client=http_client,
                    cache_adapter=self._resolve_cache_adapter(),
                )
                self.source_adapter = self.fetcher
        elif isinstance(self.source_adapter, HtmlFetcher):
            self.fetcher = self.source_adapter

        cache_adapter = self._resolve_cache_adapter()
        if cache_adapter is not None:
            if isinstance(self.source_adapter, HtmlFetcher):
                self.source_adapter.set_cache(cache_adapter)
            elif not isinstance(self.source_adapter, CacheAdapter):
                self.source_adapter = CacheAdapter(
                    source_adapter=self.source_adapter,
                    cache_adapter=cache_adapter,
                )

        return self.source_adapter
