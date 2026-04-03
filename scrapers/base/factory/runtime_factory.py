from dataclasses import dataclass
from dataclasses import replace
from typing import cast

from infrastructure.http_client.caching.file import FileCache
from infrastructure.http_client.clients.urllib_http import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_BACKOFF_SECONDS
from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.cache_adapter import CacheAdapter
from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import SourceAdapter


@dataclass(frozen=True, slots=True)
class ScraperRuntime:
    policy: HttpPolicy
    http_client: HttpClientProtocol
    cache_adapter: CacheBackend | None
    fetcher: HtmlFetcher
    source_adapter: SourceAdapter


class ScraperRuntimeFactory:
    """Buduje runtime (policy/http/cache/fetcher/source_adapter) z ScraperOptions."""

    def build(
        self,
        *,
        options: ScraperOptions,
        policy: HttpPolicy | None = None,
    ) -> ScraperRuntime:
        resolved_policy = self._resolve_policy(options=options, policy=policy)
        cache_adapter = self._resolve_cache_adapter(options)

        source_adapter = options.source_adapter
        fetcher = options.fetcher

        if isinstance(source_adapter, HtmlFetcher):
            fetcher = source_adapter
        elif isinstance(fetcher, SourceAdapter) and source_adapter is None:
            source_adapter = fetcher

        if fetcher is None and source_adapter is None:
            http_client = self._resolve_http_client(
                options=options,
                policy=resolved_policy,
            )
            fetcher = HtmlFetcher(
                policy=resolved_policy,
                http_client=http_client,
                cache_adapter=cache_adapter,
            )
            source_adapter = fetcher
        else:
            if fetcher is None and isinstance(source_adapter, HtmlFetcher):
                fetcher = source_adapter
            if fetcher is not None:
                if hasattr(fetcher, "set_cache"):
                    fetcher.set_cache(cache_adapter)
                http_client = getattr(fetcher, "http_client", None)
                if http_client is None:
                    http_client = self._resolve_http_client(
                        options=options,
                        policy=resolved_policy,
                    )
            else:
                http_client = self._resolve_http_client(
                    options=options,
                    policy=resolved_policy,
                )

            if source_adapter is None:
                source_adapter = fetcher
            elif cache_adapter is not None and not isinstance(
                source_adapter,
                HtmlFetcher,
            ):
                source_adapter = CacheAdapter(
                    source_adapter=source_adapter,
                    cache_adapter=cache_adapter,
                )

        if fetcher is None or source_adapter is None:
            msg = "Could not build scraper runtime: missing fetcher/source_adapter"
            raise ValueError(msg)

        return ScraperRuntime(
            policy=resolved_policy,
            http_client=http_client,
            cache_adapter=cache_adapter,
            fetcher=fetcher,
            source_adapter=source_adapter,
        )

    @staticmethod
    def _resolve_policy(
        *,
        options: ScraperOptions,
        policy: HttpPolicy | None,
    ) -> HttpPolicy:
        base_policy = policy or options.http.policy
        timeout = options.http.timeout
        retries = options.http.retries
        if timeout is None and retries is None:
            return base_policy
        return replace(
            base_policy,
            timeout=timeout if timeout is not None else base_policy.timeout,
            retries=retries if retries is not None else base_policy.retries,
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
            UrllibHttpClient(config=client_config),
        )

    @staticmethod
    def _resolve_cache_adapter(options: ScraperOptions) -> CacheBackend | None:
        if options.cache.cache_adapter is not None:
            return options.cache.cache_adapter
        if options.cache.cache_dir is None:
            return None
        ttl_seconds = options.cache.cache_ttl or 0
        return FileCache(
            cache_dir=options.cache.cache_dir,
            ttl_seconds=ttl_seconds,
        )
