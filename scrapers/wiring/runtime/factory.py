from typing import cast

from infrastructure.cache.file.protocol import FileCache
from infrastructure.http.clients.base import HttpClient
from infrastructure.http.config import HttpClientConfig
from infrastructure.http.policies.constants import DEFAULT_HTTP_BACKOFF_SECONDS
from infrastructure.http.policies.http import HttpPolicy
from infrastructure.http.protocols import HttpClientProtocol
from infrastructure.http.protocols.text_cache import TextCacheProtocol
from scrapers.adapters.cache_adapter import CacheAdapter
from scrapers.html_fetcher import HtmlFetcher
from scrapers.options import ScraperOptions
from scrapers.runtime.dataclass import ScraperRuntime
from scrapers.source_adapter import SourceAdapter


class SourceAdapterFetcherShim(HtmlFetcher):
    """Adapter exposing SourceAdapter as HtmlFetcher for legacy option wiring."""

    def __init__(self, source_adapter: SourceAdapter) -> None:
        self._source_adapter = source_adapter
        self.cache_adapter = None
        self.timeout = 10
        self.http_client = None
        self.policy = HttpPolicy(timeout=10, retries=0, cache=False)

    def set_cache(self, cache_adapter: TextCacheProtocol | None) -> None:
        self.cache_adapter = cache_adapter

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        _ = timeout
        return self._source_adapter.get(url)

    def get(self, url: str) -> str:
        return self._source_adapter.get(url)


class ScraperRuntimeFactory:
    """Buduje runtime (policy/http/cache/fetcher/source_adapter) z ScraperOptions."""

    def build(
        self,
        *,
        options: ScraperOptions,
        policy: HttpPolicy | None = None,
    ) -> ScraperRuntime:
        resolved_policy = options.resolve_http_policy(policy=policy)
        cache_adapter = self._resolve_cache_adapter(options)
        fetcher, source_adapter = self._resolve_fetcher_and_source_adapter(
            options=options,
            cache_adapter=cache_adapter,
            resolved_policy=resolved_policy,
        )
        http_client = self._resolve_runtime_http_client(
            options=options,
            fetcher=fetcher,
            resolved_policy=resolved_policy,
        )
        return ScraperRuntime(
            policy=resolved_policy,
            http_client=http_client,
            cache_adapter=cache_adapter,
            fetcher=fetcher,
            source_adapter=source_adapter,
        )

    def _resolve_fetcher_and_source_adapter(
        self,
        *,
        options: ScraperOptions,
        cache_adapter: TextCacheProtocol | None,
        resolved_policy: HttpPolicy,
    ) -> tuple[HtmlFetcher, SourceAdapter]:
        fetcher, source_adapter = self._normalize_runtime_components(options=options)
        if fetcher is None and source_adapter is None:
            return self._build_default_components(
                options=options,
                cache_adapter=cache_adapter,
                resolved_policy=resolved_policy,
            )
        return self._resolve_existing_components(
            fetcher=fetcher,
            source_adapter=source_adapter,
            cache_adapter=cache_adapter,
        )

    @staticmethod
    def _normalize_runtime_components(
        *,
        options: ScraperOptions,
    ) -> tuple[HtmlFetcher | None, SourceAdapter | None]:
        source_adapter = options.source_adapter
        fetcher = options.fetcher
        if isinstance(source_adapter, HtmlFetcher):
            fetcher = source_adapter
        elif isinstance(fetcher, SourceAdapter) and source_adapter is None:
            source_adapter = fetcher
        return fetcher, source_adapter

    def _build_default_components(
        self,
        *,
        options: ScraperOptions,
        cache_adapter: TextCacheProtocol | None,
        resolved_policy: HttpPolicy,
    ) -> tuple[HtmlFetcher, SourceAdapter]:
        http_client = self._resolve_http_client(
            options=options,
            policy=resolved_policy,
        )
        fetcher = HtmlFetcher(
            policy=resolved_policy,
            http_client=http_client,
            cache_adapter=cache_adapter,
        )
        return fetcher, fetcher

    @staticmethod
    def _resolve_existing_components(
        *,
        fetcher: HtmlFetcher | None,
        source_adapter: SourceAdapter | None,
        cache_adapter: TextCacheProtocol | None,
    ) -> tuple[HtmlFetcher, SourceAdapter]:
        if fetcher is None and isinstance(source_adapter, HtmlFetcher):
            fetcher = source_adapter
        if fetcher is None and source_adapter is not None:
            # Backward compatibility: allow runtime with injected source adapter only.
            fetcher = SourceAdapterFetcherShim(source_adapter)
        if fetcher is None:
            msg = "Could not build scraper runtime: missing fetcher/source_adapter"
            raise ValueError(msg)
        if hasattr(fetcher, "set_cache"):
            fetcher.set_cache(cache_adapter)
        if source_adapter is None:
            return fetcher, fetcher
        if cache_adapter is not None and not isinstance(source_adapter, HtmlFetcher):
            source_adapter = CacheAdapter(
                source_adapter=source_adapter,
                cache_adapter=cache_adapter,
            )
        return fetcher, source_adapter

    def _resolve_runtime_http_client(
        self,
        *,
        options: ScraperOptions,
        fetcher: HtmlFetcher,
        resolved_policy: HttpPolicy,
    ) -> HttpClientProtocol:
        fetcher_http_client = getattr(fetcher, "http_client", None)
        if fetcher_http_client is not None:
            return fetcher_http_client
        return self._resolve_http_client(
            options=options,
            policy=resolved_policy,
        )

    @staticmethod
    def _resolve_http_client(
        *,
        options: ScraperOptions,
        policy: HttpPolicy,
    ) -> HttpClientProtocol:
        if options.http.http_client is not None:
            return options.http.http_client

        backoff_seconds = (
            options.http.backoff_seconds
            if options.http.backoff_seconds is not None
            else DEFAULT_HTTP_BACKOFF_SECONDS
        )
        client_config = HttpClientConfig(
            timeout=policy.timeout,
            retries=policy.retries,
            backoff_seconds=backoff_seconds,
            cache=policy.cache,
        )
        return cast(
            "HttpClientProtocol",
            # di-antipattern-allow: runtime factory is the DI composition root.
            HttpClient(config=client_config),
        )

    @staticmethod
    def _resolve_cache_adapter(options: ScraperOptions) -> TextCacheProtocol | None:
        if options.cache.cache_adapter is not None:
            return options.cache.cache_adapter
        if options.cache.cache_dir is None:
            return None
        ttl_seconds = options.cache.cache_ttl or 0
        return FileCache(
            cache_dir=options.cache.cache_dir,
            ttl_seconds=ttl_seconds,
        )
